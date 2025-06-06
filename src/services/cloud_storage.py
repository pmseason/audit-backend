from google.cloud import storage
from dotenv import load_dotenv
import os

load_dotenv(override=True)


# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "audit-backend-bucket"


async def upload_file_to_bucket(file_path: str, content: str, content_type: str):
    """Uploads a file or content to the bucket.
    
    Args:
        file_path: The path where the file should be stored in the bucket
        content: string content to upload directly (HTML/MD)
        content_type: The content type of the file (text/html, text/markdown)
    """
    bucket = storage_client.bucket(bucket_name=bucket_name)
    blob = bucket.blob(file_path)
    
    # Set generation match precondition to avoid race conditions
    generation_match_precondition = 0
    
    # Upload content directly
    blob.upload_from_string(content, content_type=content_type)
    
    return f"File uploaded to {file_path}"