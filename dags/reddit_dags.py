from airflow import DAG
from airflow import settings
from airflow.models import Connection
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import os
import sys
import subprocess
import boto3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #convert relative path to absolute path
from dag_helper import default_args
#from pipelines.aws_s3_pipeline import upload_s3_pipeline
from pipelines.reddit_pipeline import reddit_pipeline_
from utils.constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION


file_postfix=datetime.now().strftime("%Y%m%d")

################################
######Secction python functions#
################################


def upload_s3_pipeline(**kwargs):
    """
    Uploads a file to an AWS S3 bucket using the Airflow S3Hook.

    Parameters:
    **kwargs: Arbitrary keyword arguments. The function expects the following keys:
        - local_path (str): The local directory path where the file is located.
        - bucket_name (str): The name of the S3 bucket where the file will be uploaded.

    Returns:
    None

    Raises:
    None

    Example Usage:
    upload_s3_pipeline(local_path='./data', bucket_name='my-s3-bucket')
    """
    #configure the connection s3
    s3_hook=S3Hook(aws_conn_id='aws_conecction')
    s3_hook.load_file(
        filename=os.path.join(kwargs['local_path'], 'reddit_extract_{}.parquet'.format(file_postfix)),
        key='reddit/bronze/reddit_extract_{}.parquet'.format(file_postfix),
        bucket_name=kwargs['bucket_name'],
        replace=True
    )
def wait_for_crawler_completion(client, crawler_name, timeout_minutes=30):
    import time
    start_time = time.time()
    while True:
        if (time.time() - start_time) > (timeout_minutes * 60):
            raise TimeoutError(f"El crawler no terminó después de {timeout_minutes} minutos")
            
        response = client.get_crawler(Name=crawler_name)
        state = response['Crawler']['State']
        
        if state == 'READY':
            last_status = response['Crawler']['LastCrawl']['Status']
            if last_status == 'SUCCEEDED':
                print("Crawler completado exitosamente")
                break
            elif last_status in ['FAILED', 'CANCELLED']:
                raise Exception(f"Crawler falló con estado: {last_status}")
                
        time.sleep(30)

def run_glue_crawler():
    """
    Runs an AWS Glue Crawler using Boto3.

    Returns:
    None

    Raises:
    None

    Example Usage:
    run_glue_crawler()
    """
    try:
        client = boto3.client('glue', 
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        
        # Verificar estado del crawler antes de iniciarlo
        crawler_info = client.get_crawler(Name='data-pipeline-dev-raw-crawler')
        current_state = crawler_info['Crawler']['State']
        
        if current_state == 'READY':
            response = client.start_crawler(Name='data-pipeline-dev-raw-crawler')
            print(f"Crawler iniciado exitosamente: {response}")
        else:
            print(f"El crawler no está listo para iniciar. Estado actual: {current_state}")
            
    except client.exceptions.CrawlerRunningException:
        print("El crawler ya está en ejecución")
    except client.exceptions.EntityNotFoundException:
        print("No se encontró el crawler especificado")
    except Exception as e:
        print(f"Error al ejecutar el crawler: {str(e)}")


#################################
#### Create new connection to AWS
#################################
def create_aws_connection():
     
    """
    Checks if an AWS connection already exists in the Airflow database.
    If the connection does not exist, it creates a new connection and adds it to the Airflow database.

    Parameters:
    None

    Returns:
    None

    Raises:
    None

    Example Usage:
    create_aws_connection()
    """
     
    session=settings.Session()
    conn_id='aws_conecction'
    existing_conn=session.query(Connection).filter(Connection.conn_id==conn_id).first()

    if existing_conn is None:
        print('Creating new connection to AWS')
    #Create connection to AWS
        aws_conn=Connection(
            conn_id=conn_id,
            conn_type='aws',
            login=AWS_ACCESS_KEY,
            password=AWS_SECRET_KEY,
            extra=f'{{"region_name": "{AWS_REGION}"}}'
        )
        #add the connection to the Airflow database    
        session.add(aws_conn)
        session.commit()
        print(f"Connection {conn_id} created successfully.")
    else:
        print(f"Connection {conn_id} already exists.")

################################
######Secction DAG##############
################################
dag=DAG(
    dag_id='etl_reddit_pipeline',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['reddit', 'etl', 'pipeline']
)

#Call new connection to AWS
connection_aws = PythonOperator(
    task_id='create_aws_connection',
    python_callable=create_aws_connection,
    dag=dag
)

#extration from reddit
extract_reddit = PythonOperator(
    task_id='reddit_extract',
    python_callable=reddit_pipeline_,
    op_kwargs={
        'file_name': 'reddit_extract_{}'.format(file_postfix),
        'subreddit': 'dataengineering',
        'time_filter': 'year',
        'limit': 100
               },
    dag=dag
)


#upload to S3
upload_s3 = PythonOperator(
    task_id='upload_s3',
    python_callable=upload_s3_pipeline,
    op_kwargs={
        'local_path': './data/output',
        'bucket_name': "data-pipeline-dev-raw-data"
    },
    dag=dag
)

#Task to run the glue crawler
# Look at the function wait_for_crawler_completion
wait_crawler_complete=PythonOperator(
    task_id='wait_crawler_complete',
    python_callable=wait_for_crawler_completion,
    dag=dag
)

# Task to run the Glue Crawler
run_glue_crawler_task = PythonOperator(
    task_id='run_glue_crawler',
    python_callable=run_glue_crawler,
    dag=dag,
)



connection_aws>>extract_reddit>>upload_s3>>wait_crawler_complete>>run_glue_crawler_task