from typing import Literal
import openai
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from loguru import logger
from browserbase import Browserbase
from playwright.async_api import async_playwright
from src.utils.utils import get_markdown_content, sanitize_url_for_filename, save_content_to_files
import base64

load_dotenv(override=True)


class ClosedRoleAuditResult(BaseModel):
    result: Literal["open", "closed", "unsure"]
    justification: str


class ClosedRoleAgent:
    def __init__(self):
        """Initialize the closed role checking agent."""
        self.client = openai.OpenAI()

    async def check_job_status(self, url: str) -> tuple[ClosedRoleAuditResult, str, bytes]:
        """
        Check if a job posting is still open or closed.
        
        Args:
            url (str): URL of the job posting to check
            
        Returns:
            tuple[ClosedRoleAuditResult, str]: A tuple containing:
                - ClosedRoleAuditResult: Object containing the status and justification
                - str: Base64 encoded screenshot of the page
        """
        async with async_playwright() as playwright:
            try:
                bb = Browserbase(api_key=os.environ["BB_API_KEY"])
                session = bb.sessions.create(project_id=os.environ["BB_PROJECT_ID"])
                chromium = playwright.chromium
                browser = await chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]
                
                try:
                    await page.goto(url)
                    html = await page.content()
                    html, markdown_content = await get_markdown_content(html)
                    save_content_to_files(html, markdown_content, f"logs/{sanitize_url_for_filename(url)}/page")
                    screenshot = await page.screenshot()
                    
                    # Convert screenshot to base64
                    screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
                    
                    # Prepare the prompt for OpenAI
                    prompt = f"""
                    Analyze the following job posting content and determine if the position is still open or closed.
                    Source URL: {url}
                    
                    Rules:
                    1. Look for indicators that the position is:
                       - "open": If the job is actively accepting applications
                       - "closed": If there are clear signs the position is no longer accepting applications
                       - "unsure": If you cannot definitively determine the status
                    2. Provide a clear justification for your decision
                    3. Look for specific phrases like:
                       - "Position closed"
                       - "No longer accepting applications"
                       - "Apply now"
                       - "Applications open"
                       - "Position filled"
                    4. Also analyze the visual elements in the screenshot for any status indicators
                    5. If there appears to be a cookie banner or popup blocking the content:
                       - Use the provided screenshot to look past/through any overlays
                       - Try to identify job status information visible in the background
                       - Note in your justification if a blocking element affected your analysis
                    
                    Content:
                    {markdown_content}
                    """
                    
                    # Call OpenAI API with structured output and vision
                    response = self.client.responses.parse(
                        model="gpt-4o-2024-08-06",
                        input=[
                            {"role": "system", "content": "You are a specialized job status checking agent that determines if job postings are still open."},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "input_text", "text": prompt},
                                    {
                                        "type": "input_image",
                                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                                    }
                                ]
                            }
                        ],
                        text_format=ClosedRoleAuditResult
                    )
                    
                    result = response.output_parsed
                    logger.info(f"Used {response.usage.total_tokens} tokens to check job status for {url}")
                    
                    return result, screenshot_base64, screenshot
                    
                except Exception as e:
                    logger.error(f"Error checking job status for {url}: {str(e)}")
                    raise
                    
            except Exception as e:
                logger.error(f"Error in browser session: {str(e)}")
                raise
                
            finally:
                await page.close() if page else None
                await browser.close() if browser else None
                logger.info(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")
