from browserbase import Browserbase
from playwright.async_api import async_playwright, Playwright
import os
from src.utils.utils import get_markdown_content
from loguru import logger

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
            return await get_markdown_content(html, url)
            
        except Exception as e:
            logger.error(f"Error extracting page content: {str(e)}")
            return None
            
        finally:
            await page.close()
            await browser.close()
            logger.info(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

    async with async_playwright() as playwright:
        return await run(playwright)

