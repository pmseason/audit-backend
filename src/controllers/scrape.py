from src.services.supabase import get_companies_with_career_page_urls
from src.agents.open_role_agent import find_open_roles
from src.agents.url_extraction_agent import URLExtractionAgent
import os
from markdownify import markdownify as md

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
    
    # for each company, call agent to scrape the role --> extract [{title, link}]
    for company in companies_to_scrape:
        try:
            response = await find_open_roles(company["career_page_link"])
            
            if not response:
                print(f"No response received for {company['name']}")
                continue
            
            html = response.get("html", "")
            
            if not html:
                print(f"No HTML content received for {company['name']}")
                continue
            
            os.makedirs("html_outputs", exist_ok=True)
            os.makedirs("markdown_outputs", exist_ok=True)
            filename = f"html_outputs/{company['name']}.html"
            markdown_filename = f"markdown_outputs/{company['name']}.md"
                
            # Write HTML content to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            
            # Convert HTML to Markdown - include common job listing tags
            markdown_content = md(html, convert=['a', 'button', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'h4', 'p', 'tr'])
            
            # Write Markdown content to file
            with open(markdown_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        
            # url_extraction_agent = URLExtractionAgent()
            # response = url_extraction_agent.extract_job_links(html, company["career_page_link"])
            # if not response:
            #     print(f"No job links found for {company['name']} at url {company['career_page_link']}")
            #     continue
                
            # job_postings = response.job_postings
            
            # print(f"Found {len(job_postings)} job links for {company['name']} at url {company['career_page_link']}")
            # print(job_postings)
            
        except Exception as e:
            print(f"Error processing {company['name']}: {str(e)}")
            continue
    
    
    