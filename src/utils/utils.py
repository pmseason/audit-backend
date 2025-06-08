import re
from src.services.cloud_storage import upload_file_to_bucket
from markdownify import markdownify as md

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


async def get_markdown_content(html: str, url: str, pathname: str = None):
    """
    Get the markdown content from a HTML string.
    """
    # Strip unwanted tags
    html = re.sub(r'<(script|img|head|style|footer)[^>]*>.*?</\1>|<(script|img|head|style|footer)[^>]*?/>', '', html, flags=re.DOTALL)
    
    # Convert HTML to Markdown
    markdown_content = md(html, convert=['a', 'button', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'p', 'tr'])
    
    # Upload files to cloud storage
    sanitized_url = sanitize_url_for_filename(url)
    filename = f"{pathname}/{sanitized_url}.html"
    markdown_filename = f"{pathname}/{sanitized_url}.md"
    
    await upload_file_to_bucket(filename, html, "text/html")
    await upload_file_to_bucket(markdown_filename, markdown_content, "text/markdown")
    
    return html, markdown_content