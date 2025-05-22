from google.cloud import tasks_v2
import os
import json
import base64
import logging
from dotenv import load_dotenv

load_dotenv(override=True)
# Initialize the client
client = tasks_v2.CloudTasksClient()

# Get configuration from environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("CLOUD_TASKS_LOCATION")
QUEUE = os.getenv("CLOUD_TASKS_QUEUE")
SERVER_URL = os.getenv("SERVER_URL")

async def create_task(payload: dict):
    """
    Create a new task in Cloud Tasks.
    
    Args:
        payload (dict): The payload to be sent with the task
        
    Returns:
        The created task response
    """
    # Construct the fully qualified queue name
    parent = client.queue_path(PROJECT_ID, LOCATION, QUEUE)

    request = tasks_v2.CreateTaskRequest(
        parent=parent,
        task={
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{SERVER_URL}/tasks/handle",
                "body": base64.b64encode(json.dumps(payload).encode()).decode(),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }
    )
    
    # Create the task
    response = client.create_task(request)
    
    return response
