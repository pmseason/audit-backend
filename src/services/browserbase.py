from dotenv import load_dotenv
import os
import asyncio
from typing import Optional
from browserbase import Browserbase
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig, BrowserSession
from langchain_anthropic import ChatAnthropic
from playwright.async_api import Page, BrowserContext as PlaywrightContext

load_dotenv(override=True)
BB_API_KEY = os.getenv("BB_API_KEY")
BB_PROJECT_ID = os.getenv("BB_PROJECT_ID")

class ExtendedBrowserSession(BrowserSession):
    """Extended version of BrowserSession that includes current_page"""
    def __init__(
        self,
        context: PlaywrightContext,
        cached_state: Optional[dict] = None,
        current_page: Optional[Page] = None
    ):
        super().__init__(context=context, cached_state=cached_state)
        self.current_page = current_page

class UseBrowserbaseContext(BrowserContext):
    async def _initialize_session(self) -> ExtendedBrowserSession:
        """Initialize a browser session using existing Browserbase page.

        Returns:
            ExtendedBrowserSession: The initialized browser session with current page.
        """
        playwright_browser = await self.browser.get_playwright_browser()
        context = await self._create_context(playwright_browser)
        # self._add_new_page_listener(context)

        self.session = ExtendedBrowserSession(
            context=context,
            cached_state=None
        )

        # Get existing page or create new one
        self.session.current_page = context.pages[0] if context.pages else await context.new_page()

        # Initialize session state
        self.session.cached_state = await self._update_state()

        return self.session
    
    

async def setup_browser() -> tuple[Browser, UseBrowserbaseContext]:
    """Set up browser and context configurations.

    Returns:
        tuple[Browser, UseBrowserbaseContext]: Configured browser and context.
    """
    bb = Browserbase(api_key=BB_API_KEY)
    bb_session = bb.sessions.create(
        project_id=BB_PROJECT_ID,
    )
    
    # # Basic configuration
# browser = Browser(
#     config=BrowserConfig(
#         headless=False,
#         disable_security=False,
#         keep_alive=True,
#         cdp_url=CDP_URL,
#         # wss_url=WSS_URL,
#         new_context_config=BrowserContextConfig(
# 			keep_alive=True,
# 			disable_security=False,
# 		),
# ))

    browser = Browser(config=BrowserConfig(cdp_url=bb_session.connect_url))
    # context = UseBrowserbaseContext(
    #     browser,
    #     BrowserContextConfig(
    #         wait_for_network_idle_page_load_time=10.0,
    #         highlight_elements=True,
    #     )
    # )

    return browser, None