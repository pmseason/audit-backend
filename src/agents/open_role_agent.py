from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from browser_use import Controller, Agent, ActionResult
from pydantic import BaseModel, Field
from typing import Optional
from src.services.browserbase import setup_browser
from markdownify import markdownify as md
from playwright.async_api import Page
from src.utils.utils import get_markdown_content, sanitize_url_for_filename, save_content_to_files
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
You are a helpful assistant that will help search for and load job listings. You will be provided with:
- job_title: The title or role to search for
- url: The url of the page you are on

Do not:
- Navigate away from the search results page
- Click on individual job listings
- Click pagination links

The goal is to get all relevant job listing links loaded into the current page DOM for later scraping.
"""

async def on_step_end(agent: Agent, original_url: str):
    html = await agent.browser_context.get_page_html()
    page = await agent.browser_context.get_agent_current_page()
    agent.html = html
async def find_open_roles(url: str, job_title: str):
    clean_url = sanitize_url_for_filename(url)
    initial_actions = [
        {'open_tab': {'url': url}},
    ]
    
    # Define task instructions dynamically with the job_title
    task_instructions = f"""
Your task is to:
1. Locate the job search form on the page
2. Enter the job_title: {job_title} into the primary search field.
3. Leave the other filters/fields blank
4. Submit the search form
5. Hit enter to submit the search, or click the search button
6. Once results load, scroll to bottom and click any "Load More" buttons to ensure all matching jobs are loaded in the DOM
7. Dismiss any cookie banners or popups that appear
8. Do not navigate away from the site, or click any other links, including pagination.
"""
    
    browser = None
    context = None
    
    try:
        # Initialize browser
        browser, _ = await setup_browser()
        
        agent = Agent(
            task=task_instructions,
            context=MESSAGE_CONTEXT,
            llm=llm,
            browser=browser,
            initial_actions=initial_actions,
            controller=controller,
            use_vision=True,
            save_conversation_path=f"logs/{clean_url}/"
        )
        
        history = await agent.run(
            max_steps=10,
            on_step_end=lambda agent: on_step_end(agent, url)
        )
        
        # Get the final HTML from the last step
        html = getattr(agent, 'html', "")
        
        # Strip img and script tags from HTML before processing
        if html:
            html, markdown_content = await get_markdown_content(html)
            save_content_to_files(html, markdown_content, f"logs/{clean_url}/page")
        
        tokens = history.total_input_tokens()
        logger.info(f'Tokens: {tokens}')
        
        # Return both the result and the final HTML
        return html, markdown_content
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
    finally:
        if browser:
            await browser.close()