import dotenv
import os
import httpx

dotenv.load_dotenv()

DIRECTUS_TOKEN = os.getenv("DIRECTUS_API_KEY")
base_url = "https://directus.apmseason.com"

async def add_position_to_directus(position: dict):
    """
    Add a position to Directus by posting to /items/positions endpoint
    
    Args:
        position (dict): The position data to add
        
    Returns:
        dict: The response from Directus
    """
    headers = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/items/positions",
            json=position,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

async def update_position_in_directus(position_id: str, new_position: dict):
    """
    Update a position in Directus by patching to /items/positions/{id} endpoint
    
    Args:
        position_id (str): The ID of the position to update
        new_position (dict): The updated position data
        
    Returns:
        dict: The response from Directus
    """
    headers = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{base_url}/items/positions/{position_id}",
            json=new_position,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    