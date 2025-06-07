from browserbase import Browserbase
from playwright.async_api import async_playwright, Playwright
from markdownify import markdownify as md
import os
import re
from src.services.cloud_storage import upload_file_to_bucket
from src.utils.utils import sanitize_url_for_filename


async def extract_page_content(url: str):
    """
    Extract HTML content from a URL using Browserbase and convert it to markdown.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        dict: A dictionary containing the HTML and markdown content
    """
    bb = Browserbase(api_key=os.environ["BB_API_KEY"])

    async def run(playwright: Playwright):
        # Create a session on Browserbase
        session = bb.sessions.create(project_id=os.environ["BB_PROJECT_ID"])

        # Connect to the remote session
        chromium = playwright.chromium
        browser = await chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        try:
            # Navigate to the URL
            await page.goto(url)
            
            # Get the HTML content
            html = await page.content()
            
            # Strip unwanted tags
            html = re.sub(r'<(script|img|head|style|footer)[^>]*>.*?</\1>|<(script|img|head|style|footer)[^>]*?/>', '', html, flags=re.DOTALL)
            
            # Convert HTML to Markdown
            markdown_content = md(html, convert=['a', 'button', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'p', 'tr'])
            
            # Upload files to cloud storage
            sanitized_url = sanitize_url_for_filename(url)
            filename = f"job_extraction/{sanitized_url}.html"
            markdown_filename = f"job_extraction/{sanitized_url}.md"
            
            await upload_file_to_bucket(filename, html, "text/html")
            await upload_file_to_bucket(markdown_filename, markdown_content, "text/markdown")
            
            return html, markdown_content
        except Exception as e:
            print(f"Error extracting page content: {str(e)}")
            return None, None
            
        finally:
            await page.close()
            await browser.close()
            print(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

    async with async_playwright() as playwright:
        return await run(playwright)

