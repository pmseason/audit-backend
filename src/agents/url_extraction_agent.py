from typing import List, Dict
import openai
from urllib.parse import urljoin
import re
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv(override=True)

class JobLinks(BaseModel):
    """Model for structured job link output."""
    job_postings: List[str] = Field(default_factory=list, description="Direct links to specific job postings")

class URLExtractionAgent:
    def __init__(self):
        """Initialize the URL extraction agent."""
        self.client = openai.OpenAI()
        
    def extract_job_links(self, markdown_content: str, source_url: str) -> JobLinks:
        """
        Extract job-related links from Markdown content.
        
        Args:
            markdown_content (str): The Markdown content to analyze
            source_url (str): The source URL of the Markdown content
            
        Returns:
            JobLinks: A Pydantic model containing categorized job links
        """
        # Prepare the prompt for OpenAI
        prompt = f"""
        Analyze the following Markdown content and extract all job or application links. 
        Source URL: {source_url}
        
        Rules:
        1. Only extract links that are likely to be job postings, these usually have an ID or a job-related keyword in the URL
        2. Ignore social media links, navigation links, or general website pages
        3. Categorize the links into:
           - job_postings: Direct links to job postings
        
        Markdown Content:
        {markdown_content}
        """
        
        try:
            # Call OpenAI API with structured output
            response = self.client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": "You are a specialized URL extraction agent that identifies job-related links from HTML content."},
                    {"role": "user", "content": prompt}
                ],
                text_format=JobLinks
            )
            
            # Parse the response into JobLinks model
            job_links = response.output_parsed
            
            if not job_links:
                return None
            
            job_links.job_postings = [urljoin(source_url, url) for url in job_links.job_postings]
            
            return job_links
            
        except Exception as e:
            print(f"Error extracting job links: {str(e)}")
            return None
