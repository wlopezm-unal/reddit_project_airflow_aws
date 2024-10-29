import praw
from praw import Reddit
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.constants import POST_FIELDS

def connect_reddit(client_id, secret, user_agent)-> Reddit:
    """
    Connect to the Reddit API using PRAW.

    Args:
        client_id : The client ID of your Reddit application.
        secret : The client secret of your Reddit application.
        user_agent (str): A unique identifier that helps Reddit identify the source of the requests.

    Returns:
        praw.Reddit: An instance of the PRAW Reddit object.

    Raises:
        SystemExit: If there is an error connecting to the Reddit API.
    """
    
    try:
        reddit=praw.Reddit(client_id=client_id,
                           client_secret=secret,
                           user_agent=user_agent)
        print("connected to reddit")
        return reddit
    except Exception as e:
        print("Error connecting to Reddit API")
        print(e)
        sys.exit(1) #This indicates that the program should exit with an error code of 1

def extract_posts(reddit_instance: Reddit, subreddit: str, time_filter: str, limit: int):
    """
    Extracts top posts from a specified subreddit using the Reddit API.

    Args:
        reddit_instance (Reddit): An instance of the PRAW Reddit class used to interact with the Reddit API.
        subreddit (str): The name of the subreddit from which to extract posts.
        time_filter (str): The time filter to apply when extracting top posts (e.g., 'day', 'week', 'month').
        limit (int): The maximum number of posts to extract.

    Returns:
        list: A list of dictionaries, each containing the filtered attributes of a post.
    """
    # Get the subreddit instance
    subreddit_instance = reddit_instance.subreddit(subreddit)
    # Retrieve the top posts from the subreddit based on the time filter and limit
    posts = subreddit_instance.top(time_filter=time_filter, limit=limit)

    # Initialize an empty list to store the filtered posts
    post_lists = []
    for post in posts:
        # Convert the post object to a dictionary
        post_dict = vars(post)
        print(post_dict)
        # Filter the post dictionary to include only the specified fields
        filtered_post = {key: post_dict[key] for key in POST_FIELDS if key in post_dict}
         # Append the filtered post to the list of posts
        post_lists.append(filtered_post)


    return post_lists

def trasnsform_data(post_df:pd.DataFrame):
    """
    Transforms the DataFrame by converting Unix timestamps to datetime and boolean values to strings.

    Args:
        post_df (pd.DataFrame): The DataFrame containing Reddit post data.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """

    #convert Unix timestamps to datetime
    post_df['created_utc'] = pd.to_datetime(post_df['created_utc'], unit='s')
    #convert the boolean values to string (Yes or No)
    post_df['over_18'] = np.where(post_df['over_18']==True, 'Yes', 'No')
    post_df['author']=post_df['author'].astype(str)
    post_df['edited']=post_df['edited'].astype(str)
    edited_mode=post_df['edited'].mode()[0] #Calcule the mode of the column
    post_df['edited'] = np.where(post_df['edited'].isin(['True', 'False']), post_df['edited'], edited_mode).astype(bool)
    post_df['num_comments']=post_df['num_comments'].astype(int)
    post_df['score']=post_df['score'].astype(int)
    post_df['selftext']=post_df['selftext'].astype(str)
    post_df['spoiler']=post_df['spoiler'].astype(bool)
    post_df['score']=post_df['score'].astype(int)
    return post_df

def load_data_to_parquet(post_df:pd.DataFrame, path:str):
    """
    Loads the DataFrame to a Parquet file.

    Args:
        post_df (pd.DataFrame): The DataFrame containing Reddit post data.
        file_path (str): The path where the Parquet file will be saved.
    """
    post_df.to_parquet(path, index=False)
    print(f'Data successfully saved to {path}')
