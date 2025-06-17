import re
import os
from urllib.parse import urlparse
from src.services.cloud_storage import upload_file_to_bucket
from markdownify import markdownify as md

def sanitize_url_for_filename(url: str) -> str:
    """
    Sanitize a URL to be used as a filename by replacing forward slashes and other unsafe characters.
    The result will contain the domain name and up to 30 characters from the path and query parameters.
    
    Args:
        url (str): The URL to sanitize
        
    Returns:
        str: A sanitized string safe for use in filenames
    """
    # Parse the URL using urllib
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split('/')[0]  # fallback to first path segment if no domain
    
    # Combine path and query parameters
    path_and_query = parsed.path.lstrip('/')
    if parsed.query:
        path_and_query += '?' + parsed.query
    
    # Take up to 30 characters from the combined path and query
    path_and_query = path_and_query[:50]
    
    # Combine domain and path, then sanitize
    combined = f"{domain}_{path_and_query}"
    # Remove any potentially problematic characters
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', combined)
    return sanitized

def save_content_to_files(html_content: str, markdown_content: str, pathname: str) -> None:
    """
    Save HTML and markdown content to files.
    
    Args:
        html_content (str): The HTML content to save
        markdown_content (str): The markdown content to save
        pathname (str): The base pathname for the files (without extension)
    """
    html_filename = f"{pathname}.html"
    markdown_filename = f"{pathname}.md"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(html_filename), exist_ok=True)
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    os.makedirs(os.path.dirname(markdown_filename), exist_ok=True)
    with open(markdown_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

async def get_markdown_content(html: str):
    """
    Get the markdown content from a HTML string and save to files.
    
    Args:
        html (str): The HTML content to process
        
    Returns:
        tuple[str, str]: A tuple containing (html_content, markdown_content)
    """
    # Strip unwanted tags
    cleaned_html = re.sub(r'<(script|img|head|style|footer)[^>]*>.*?</\1>|<(script|img|head|style|footer)[^>]*?/>', '', html, flags=re.DOTALL)
    
    # Convert HTML to Markdown
    markdown_content = md(cleaned_html, convert=['a', 'button', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'p', 'tr'])
    
    return cleaned_html, markdown_content



# print(sanitize_url_for_filename("https://lifeattiktok.com/search?keyword=product+manager+intern&recruitment_id_list=&job_category_id_list=6704215864629004552&subject_id_list=7322364514224687370%2C7322364513776093449%2C7459987887569733896%2C7459986622530078983&location_code_list=&limit=12&offset=0"))