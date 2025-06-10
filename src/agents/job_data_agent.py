from typing import Optional
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger
from src.types.audit import ScrapedJobAgent

load_dotenv(override=True)




class JobDataAgent:
    def __init__(self):
        """Initialize the job data extraction agent."""
        self.client = openai.OpenAI()
        
    def extract_job_data(self, markdown_content: str, source_url: str) -> Optional[ScrapedJobAgent]:
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
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None
