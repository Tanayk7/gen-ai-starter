import json
import aiohttp
import boto3
import os 
import concurrent.futures
from dotenv import load_dotenv

load_dotenv() 

def process_requests_concurrently(requests, execution_handler, num_workers=5):
    results = []
    # Using ThreadPoolExecutor to handle multiple requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submitting process_gpt with the prompt, system_msg, and (image_path / cv2_image /url)
        results = list(executor.map(lambda params: execution_handler(**params), requests))
    return results

def json_to_dict(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
# Asynchronous function to send a single POST request
async def request_post(url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()

async def request_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def load_json_in_chunks(data, chunk_size=100):
    print("Total comments: ", len(data))
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]  # Yield chunks of the array


def save_text_to_s3(s3_key, text, bucket_name): 
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    try:
        # Initialize S3 client
        s3_client = session.client("s3")
        # Save data to a file on s3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=text,
            ContentType="text/html"  # Ensure the correct content type for HTML files
        )
        # Construct and return the object URL
        region = os.getenv("AWS_DEFAULT_REGION")
        object_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        return object_url
    except Exception as e:
        raise Exception(f"Falied to save file to S3. Error: {e}")

def get_s3_file_content(s3_key, region_name='ap-south-1'):
    """
    Fetch the text content of a file from S3.
    Args:
        s3_key (str): The key (path) to the file in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.
        region_name (str, optional): The AWS region where the S3 bucket is hosted. Defaults to 'ap-south-1'.

    Returns:
        str: The text content of the file.

    Raises:
        Exception: If the file cannot be fetched or read.
    """
    # Explicitly provide credentials
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    try:
        # Initialize S3 client
        s3_client = session.client("s3")
        # Fetch the file object
        response = s3_client.get_object(Bucket=os.getenv('AWS_S3_BUCKET_NAME'), Key=s3_key)
        # Read and return the file content as a string
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to get file content from S3. Error: {e}")