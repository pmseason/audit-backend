import re
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


# print(sanitize_url_for_filename("https://lifeattiktok.com/search?keyword=product+manager+intern&recruitment_id_list=&job_category_id_list=6704215864629004552&subject_id_list=7322364514224687370%2C7322364513776093449%2C7459987887569733896%2C7459986622530078983&location_code_list=&limit=12&offset=0"))