from src.services.supabase import get_companies_with_career_page_urls
from src.agents.open_role_agent import find_open_roles
from src.agents.url_extraction_agent import URLExtractionAgent
import os
from markdownify import markdownify as md
from src.services.cloud_storage import upload_file_to_bucket
from src.services.playwright import extract_page_content
from src.agents.job_data_agent import JobDataAgent
from src.services.supabase import insert_scraped_jobs
from loguru import logger


        
        
        
async def get_job_postings(url: str, taskId: str = None, site: str = None):
    try:
        html, markdown_content = await find_open_roles(url)
        
        if not html or not markdown_content:
            logger.error(f"No response received for {url}")
            return
        
        url_extraction_agent = URLExtractionAgent()
        response = url_extraction_agent.extract_job_links(markdown_content, url)
            
        job_postings = response.job_postings if response else []
        
        scraped_jobs = []
        
        for job_posting in job_postings:
            logger.info(f"Extracting job data for {job_posting}")
            html, markdown_content = await extract_page_content(job_posting)
            if not html or not markdown_content:
                logger.error(f"No response received for {job_posting}")
                continue
            
            job_data_agent = JobDataAgent()
            response = job_data_agent.extract_job_data(markdown_content, job_posting)
            job = response.model_dump() if response else None
            if job:
                logger.info(f"Successfully extracted data for {job_posting}")
                logger.info(f"Job: {job}")
                scraped_jobs.append(job)
                await insert_scraped_jobs([job], taskId)
            
        return scraped_jobs
        
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        return []
    
    
    