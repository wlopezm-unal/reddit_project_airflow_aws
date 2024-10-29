from etls.reddit_etl import connect_reddit, extract_posts, trasnsform_data, load_data_to_parquet
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.constants import CLIENT_ID, SECRET, OUTPUT_PATH

def reddit_pipeline_(file_name:str, subreddit:str, time_filter:str, limit:None):
    """
        Uploads a file to an AWS S3 bucket using the Airflow S3Hook.

        Parameters:
        file_name (str): The name of the output file (without extension).
        subreddit (str): The name of the subreddit to extract posts from.
        time_filter (str): The time filter for the posts (e.g., 'day', 'week', 'month', 'year', 'all').
        limit (int or None): The maximum number of posts to extract. If None, all available posts are extracted.

        Returns:
        str: The path to the output Parquet file.

        Raises:
        None

        Example Usage:
        upload_s3_pipeline(local_path='./data', bucket_name='my-s3-bucket')
    """
    
    ###connecting instance
    instance=connect_reddit(client_id=CLIENT_ID, secret=SECRET, user_agent='AirScholar') 

    ###extraction
    print('initiating extraction process')
    posts = extract_posts(reddit_instance=instance, 
                          subreddit=subreddit, 
                          time_filter=time_filter, 
                          limit=limit)
    post_df = pd.DataFrame(posts)

    ###transformation
    post_df=trasnsform_data(post_df)

    ##loading to Parquet format
    # Ensure the output directory exists
    output_dir = OUTPUT_PATH
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path=f'{output_dir}/{file_name}.parquet'
    load_data_to_parquet(post_df, file_path)

    return file_path
    