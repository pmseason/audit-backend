from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import re
from browser_use import BrowserConfig, Browser, Controller, Agent, BrowserContextConfig, ActionResult
from pydantic import BaseModel, Field
from typing import Literal, Optional
from src.agents.agent_logging import record_activity
from src.services.browserbase import setup_browser
from markdownify import markdownify as md
from src.services.cloud_storage import upload_file_to_bucket
import os
from playwright.async_api import Page
from playwright.sync_api import sync_playwright, Playwright
from browserbase import Browserbase
from src.utils.utils import get_markdown_content, sanitize_url_for_filename
from loguru import logger

# Load environment variables
load_dotenv(override=True)
# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

class DismissPopupParams(BaseModel):
    accept_css_selector: Optional[str] = Field(
        default=None,
        description="CSS selector for the accept/agree button in cookie banners or popups"
    )
    dismiss_css_selector: Optional[str] = Field(
        default=None,
        description="CSS selector for the dismiss/close button in popups"
    )


# controller = Controller(output_model=OpenRoleAuditTask, exclude_actions=["go_to_url"])
controller = Controller(exclude_actions=["go_to_url"])

@controller.action('Dismiss a cookie banner or popup', param_model=DismissPopupParams)
async def dismiss_popup(params: DismissPopupParams, page: Page) -> ActionResult:
    if params.accept_css_selector:
        try:
            await page.click(params.accept_css_selector)
            return ActionResult(extracted_content=f"Clicked accept button using selector: {params.accept_css_selector}")
        except Exception as e:
            return ActionResult(extracted_content=f"Failed to click accept button: {str(e)}")
    
    if params.dismiss_css_selector:
        try:
            await page.click(params.dismiss_css_selector)
            return ActionResult(extracted_content=f"Clicked dismiss button using selector: {params.dismiss_css_selector}")
        except Exception as e:
            return ActionResult(extracted_content=f"Failed to click dismiss button: {str(e)}")
    
    return ActionResult(extracted_content="No selectors provided for dismissal")

MESSAGE_CONTEXT = """
You are a helpful assistant that will help scrape job listings. All you have to do
is navigate to the bottom of each page to load all jobs into the current DOM. If a cookie banner or popup appears, dismiss it.
If you see a "Load more" button at the bottom of the page, click it a few times.
Do not navigate away from the site, or click any other links, including pagination.
"""

async def on_step_end(agent: Agent):
    html = await agent.browser_context.get_page_html()
    page = await agent.browser_context.get_agent_current_page()
    
    current_url = page.url
    visit_log = agent.state.history.urls()
    previous_url = visit_log[-2] if len(visit_log) >= 2 else None
    
    if current_url != previous_url:
        # Store only the current HTML per page
        agent.html = html

async def find_open_roles(url: str):
    clean_url = sanitize_url_for_filename(url)
    initial_actions = [
        {'open_tab': {'url': url}},
    ]
    
    browser = None
    context = None
    
    try:
        # Initialize browser
        browser, _ = await setup_browser()
        
        agent = Agent(
            task=MESSAGE_CONTEXT,
            llm=llm,
            browser=browser,
            initial_actions=initial_actions,
            controller=controller,
            use_vision=True,
            save_conversation_path=f"logs/{clean_url}/"
        )
        
        history = await agent.run(
            max_steps=8,
            on_step_end=on_step_end
        )
        
        # Get the final HTML from the last step
        html = getattr(agent, 'html', "")
        
        # Strip img and script tags from HTML before processing
        if html:
            html, markdown_content = await get_markdown_content(html, url, "url_extraction")
        
        tokens = history.total_input_tokens()
        logger.info(f'Tokens: {tokens}')
        
        # Return both the result and the final HTML
        return html, markdown_content
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None, None
    finally:
        if browser:
            await browser.close()