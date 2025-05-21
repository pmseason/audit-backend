from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
from browser_use import BrowserConfig, Browser, Controller, Agent, BrowserContextConfig
from pydantic import BaseModel
from typing import Literal
from src.agents.agent_logging import record_activity
import os

# Load environment variables
load_dotenv(override=True)
CDP_URL = os.getenv("CDP_URL", "http://localhost:9222")
WSS_URL = os.getenv("WSS_URL")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Basic configuration
browser = Browser(
    config=BrowserConfig(
        headless=False,
        disable_security=False,
        keep_alive=True,
        cdp_url=CDP_URL,
        # wss_url=WSS_URL,
        new_context_config=BrowserContextConfig(
			keep_alive=True,
			disable_security=False,
		),
))



class ClosedRoleAuditTask(BaseModel):
    result: Literal["open", "closed", "unsure"]
    justification: str

controller = Controller(output_model=ClosedRoleAuditTask)


MESSAGE_CONTEXT = """
You are a helpful assistant that checks the status of a job posting.

You will be given a URL to a job posting.

Use the context clues around the page to determine if the role is closed or open.

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
    
    # Initialize browser
    
    agent = Agent(
        task=MESSAGE_CONTEXT,
        llm=llm,
        browser=browser,
        initial_actions=initial_actions,
        controller=controller,
        use_vision=False,
        save_conversation_path="recordings/"
    )
    # history = await agent.run(max_steps=3, on_step_end=record_activity)
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
        