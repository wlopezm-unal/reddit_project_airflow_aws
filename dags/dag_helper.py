from datetime import datetime, timedelta


default_args = {
    'owner': 'Wilber Lopez',
    'depends_on_past': False,
    'email': ['wlopezm@unal.edu.co'],
    'email_on_failure': False,
    'email_on_retry': False,    
    'start_date': datetime(2024, 1, 1),
    'retries': 1
    #'retry_delay': timedelta(minutes=5) #this allows that the task will be retried after 5 minutes, but it is not necessary in the moment
}