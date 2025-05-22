from typing import Iterable
from google.cloud import compute_v1

from dotenv import load_dotenv

load_dotenv(override=True)
# Initialize the client
client = tasks_v2.CloudTasksClient()

# Get configuration from environment variables
PROJECT_ID = os.getenv("CLOUD_TASKS_PROJECT_ID")
LOCATION = os.getenv("CLOUD_TASKS_LOCATION")
INSTANCE_ID = os.getenv("INSTANCE_ID")


def list_instances(project_id: str, zone: str) -> Iterable[compute_v1.Instance]:
    """
    List all instances in the given zone in the specified project.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone you want to use. For example: "us-west3-b"
    Returns:
        An iterable collection of Instance objects.
    """
    instance_client = compute_v1.InstancesClient()
    instance_list = instance_client.list(project=project_id, zone=zone)

    print(f"Instances found in zone {zone}:")
    for instance in instance_list:
        print(f" - {instance.name} ({instance.machine_type})")

    # instance_list is a generator, so we need to return a list if it will be used multiple times
    return instance_list
