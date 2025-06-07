import re

def sanitize_url_for_filename(url: str) -> str:
    """
    Sanitize a URL to be used as a filename by replacing forward slashes and other unsafe characters.
    
    Args:
        url (str): The URL to sanitize
        
    Returns:
        str: A sanitized string safe for use in filenames
    """
    # Replace forward slashes with underscores
    sanitized = url.replace('/', '_')
    # Remove any other potentially problematic characters
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', sanitized)
    return sanitized