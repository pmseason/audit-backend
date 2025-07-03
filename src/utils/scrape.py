from src.agents.open_role_agent import find_open_roles
from src.agents.url_extraction_agent import URLExtractionAgent
import os
from markdownify import markdownify as md
from src.agents.job_data_agent import JobDataAgent
from src.services.supabase import insert_scraped_jobs, filter_jobs_to_scrape
from loguru import logger
from fastapi import HTTPException

        
        
        
async def get_job_postings(url: str, taskId: str, company_id: str, role_type: str, site: str, job_title: str):
    try:
        html, markdown_content = await find_open_roles(url, job_title)
        
        if not html or not markdown_content:
            logger.error(f"No response received for {url}")
            raise HTTPException(status_code=404, detail="No response received for url")
        
        url_extraction_agent = URLExtractionAgent()
        response = url_extraction_agent.extract_job_links(markdown_content, url)
            
        job_postings = response.job_postings if response else []
        
        
        logger.info(f"Found {len(job_postings)} job postings")
        
        job_postings = await filter_jobs_to_scrape(job_postings)
        logger.info(f"Adding {len(job_postings)} job postings to scrape")
        
        job_data_agent = JobDataAgent()
        jobs = await job_data_agent.extract_page_content(job_postings, url)
        
        for job in jobs:
            # Set site based on job type flags
            if job.get("is_product_job") == True:
                job["site"] = "apm"
            elif job.get("is_consulting_job") == True:
                job["site"] = "consulting"
            elif job.get("is_swe_job") == True:
                job["site"] = "swe"
            elif job.get("is_other_job") == True:
                job["site"] = "other"
            else:
                job["site"] = "other"
            
            # remove keys that dont align with db schema
            job.pop("is_product_job")
            job.pop("is_consulting_job")
            job.pop("is_swe_job")
            job.pop("is_other_job")
            
            job["company"] = company_id
            job["scraping_task"] = taskId
        
        if jobs and len(jobs) > 0:
            await insert_scraped_jobs(jobs)
            
        return jobs
        
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    