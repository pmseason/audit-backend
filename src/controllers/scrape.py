from src.services.supabase import get_companies_with_career_page_urls
from src.agents.open_role_agent import find_open_roles
from src.agents.url_extraction_agent import URLExtractionAgent
import os
from markdownify import markdownify as md
from src.services.cloud_storage import upload_file_to_bucket
from src.services.playwright import extract_page_content
from src.agents.job_data_agent import JobDataAgent

async def start_scrape_role():
    # fetch companies with defined urls
    companies_to_scrape = [
    #     {
    #     "name": "Roblox_0",
    #     "career_page_link": "https://careers.roblox.com/jobs?search=product&page=1&pageSize=9"
    # },
    #                        {
    #     "name": "Roblox_1",
    #     "career_page_link": "https://careers.roblox.com/jobs?search=product&page=2&pageSize=9"
    # },
    #                        {
    #     "name": "Roblox_2",
    #     "career_page_link": "https://careers.roblox.com/jobs?search=product&page=3&pageSize=9"
    # },
    # {
    #     "name": "Uber",
    #     "career_page_link": "https://www.uber.com/us/en/careers/list/?query=product"
    # },
    # {
    #     "name": "Corsair",
    #     "career_page_link": "https://edix.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?keyword=product&lastSelectedFacet=LOCATIONS&selectedLocationsFacet=300000000361862"
    # }
    # {
    #     "name": "Zoom",
    #     "career_page_link": "https://careers.zoom.us/jobs/search?query=product"
    # },
    {
        "name": "Yelp",
        "career_page_link": "https://www.yelp.careers/us/en/search-results?keywords=product"
    }
    ]
        
        
        
async def get_job_postings(url: str):
    try:
        html, markdown_content = await find_open_roles(url)
        
        if not html or not markdown_content:
            print(f"No response received for {url}")
            return
        
        url_extraction_agent = URLExtractionAgent()
        response = url_extraction_agent.extract_job_links(markdown_content, url)
            
        job_postings = response.job_postings if response else []
        
        scraped_jobs = []
        
        for job_posting in job_postings:
            html, markdown_content = await extract_page_content(job_posting)
            if not html or not markdown_content:
                print(f"No response received for {job_posting}")
                continue
            
            job_data_agent = JobDataAgent()
            response = job_data_agent.extract_job_data(markdown_content, job_posting)
            job =  {
                "title": response.title,
                "location": response.location,
                "url": job_posting,
                "description": response.description,
                "company": response.company,
                "other": response.other
            } if response else None
            if job:
                scraped_jobs.append(job)
            
        return scraped_jobs
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return []
    
    
    