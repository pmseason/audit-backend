from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
from browser_use import BrowserConfig, Browser, Controller, Agent, BrowserContextConfig, ActionResult
from pydantic import BaseModel, Field
from typing import Literal, Optional
from src.agents.agent_logging import record_activity
from src.services.browserbase import setup_browser
import os
from playwright.async_api import Page

# Load environment variables
load_dotenv(override=True)
CDP_URL = os.getenv("CDP_URL", "http://localhost:9222")
WSS_URL = os.getenv("WSS_URL")

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

class ClosedRoleAuditTask(BaseModel):
    result: Literal["open", "closed", "unsure"]
    justification: str

controller = Controller(output_model=ClosedRoleAuditTask, exclude_actions=["go_to_url"])

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
You are a helpful assistant that checks the status of a job posting.

You will be given a URL to a job posting.

Use the context clues around the page to determine if the role is closed or open.

If there is any cookie banner, you can click the "Accept all" button to close it.

You are to respond with the following structure:
{
    "result": "open" | "closed" | "unsure",
    "justification": "A short explanation for your answer"
}

Some hints that the role is closed:
- There is text on the page that indicates the role is closed
- There is a message on the page that indicates the role is closed

Some hints that the role is open:
- There is text on the page that indicates the role is open
- There is an "Apply" button on the page
- The text content on the page describes any of the following: the role, location, interview structure, application process, salary, technology stack, or other details

You can scroll through the page to get more context.


"""


async def check_closed_role(url: str):
    initial_actions = [
	    {'open_tab': {'url': url}},
    ]
    
    browser = None
    context = None
    
    try:
        # Initialize browser
        browser, _ = await setup_browser()
        # session = await context.get_session()
        
        agent = Agent(
            task=MESSAGE_CONTEXT,
            llm=llm,
            browser=browser,
            # browser_context=context,
            initial_actions=initial_actions,
            controller=controller,
            use_vision=False,
            save_conversation_path="recordings/"
        )
        
        history = await agent.run(max_steps=5)
        
        result = history.final_result()
        screenshot = history.screenshots()[0]
        tokens = history.total_input_tokens()
        print(f'Tokens: {tokens}')
        
        if result:
            parsed = ClosedRoleAuditTask.model_validate_json(result)
            print('\n--------------------------------')
            print(f'Result:       {parsed.result}')
            print(f'Justification: {parsed.justification}')
            return parsed, screenshot
        else:
            print('No result')
            return None, None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None
    finally:
        if browser:
            await browser.close()
        