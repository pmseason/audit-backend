from typing import Optional, List, Dict
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger
from src.types.audit import ScrapedJobAgent
from browserbase import Browserbase
from playwright.async_api import async_playwright, Playwright
from src.utils.utils import get_markdown_content

load_dotenv(override=True)


class JobDataAgent:
    def __init__(self):
        """Initialize the job data extraction agent."""
        self.client = openai.OpenAI()

    async def fetch_markdown_contents(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Fetch markdown content from multiple URLs using Browserbase.
        
        Args:
            urls (List[str]): List of URLs to fetch content from
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing URL and markdown content
        """
        async with async_playwright() as playwright:
            try:
                bb = Browserbase(api_key=os.environ["BB_API_KEY"])
                session = bb.sessions.create(project_id=os.environ["BB_PROJECT_ID"])
                chromium = playwright.chromium
                browser = await chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]
                
                markdown_contents = []
                
                for url in urls:
                    try:
                        await page.goto(url)
                        html = await page.content()
                        html, markdown_content = await get_markdown_content(html, url, "job_extraction")
                        logger.info(f"Fetched markdown content from {url}")
                        markdown_contents.append({
                            "url": url,
                            "markdown": markdown_content
                        })
                    except Exception as e:
                        logger.error(f"Error fetching content from {url}: {str(e)}")
                        continue
                
                return markdown_contents
                    
            except Exception as e:
                logger.error(f"Error in browser session: {str(e)}")
                raise
                    
            finally:
                await page.close() if page else None
                await browser.close() if browser else None
                logger.info(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

    async def process_markdown_contents(self, markdown_contents: List[Dict[str, str]]) -> List[Dict]:
        """
        Process markdown contents through OpenAI to extract job data.
        
        Args:
            markdown_contents (List[Dict[str, str]]): List of dictionaries containing URL and markdown content
            
        Returns:
            List[Dict]: List of processed job data
        """
        jobs = []
        
        for content in markdown_contents:
            job_data = await self.parse_page_with_ai(content["markdown"], content["url"])
            if job_data:
                job_dict = job_data.model_dump()
                job_dict["url"] = content["url"]
                jobs.append(job_dict)
        
        return jobs

    async def extract_page_content(self, urls: List[str]):
        """
        Main method to extract job data from multiple URLs.
        
        Args:
            urls (List[str]): List of URLs to process
            
        Returns:
            List[Dict]: List of processed job data
        """
        markdown_contents = await self.fetch_markdown_contents(urls)
        return await self.process_markdown_contents(markdown_contents)

    async def parse_page_with_ai(self, markdown_content: str, source_url: str) -> Optional[ScrapedJobAgent]:
        """
        Extract job data from Markdown content.
        
        Args:
            markdown_content (str): The Markdown content to analyze
            source_url (str): The source URL of the Markdown content
            
        Returns:
            Optional[ScrapedJob]: A ScrapedJob object containing the extracted data, or None if extraction fails
        """
        # Prepare the prompt for OpenAI
        prompt = f"""
        Analyze the following Markdown content and extract job-related information.
        Source URL: {source_url}
        
        Rules:
        1. Extract all relevant job information including title, company, location, salary, visa sponsored, job type, and description
        2. If certain information is not available, leave it blank
        3. If the job is not a product-related or consulting-related job, set the site to "other"
        4. If the job is a product-related job, set the site to "apm"
        5. If the job is a consulting-related job, set the site to "consulting"
        
        Markdown Content:
        {markdown_content}
        """
        
        try:
            # Call OpenAI API with structured output
            response = self.client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": "You are a specialized job data extraction agent that identifies and structures job-related information from content."},
                    {"role": "user", "content": prompt}
                ],
                text_format=ScrapedJobAgent
            )
            
            # Parse the response into ScrapedJob model
            job_data = response.output_parsed
            
            logger.info(f"Used {response.usage.total_tokens} tokens to extract job data from {source_url}")
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            raise
