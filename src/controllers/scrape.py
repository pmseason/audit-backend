from src.utils.scrape import get_job_postings
from loguru import logger
from src.utils.logging_config import setup_logging, upload_logs_to_cloud
from src.utils.utils import sanitize_url_for_filename

async def start_scrape_roles():
    # fetch companies with defined urls
    companies_to_scrape = [
    {
        "name": "Yelp",
        "link": "https://www.yelp.careers/us/en/search-results?keywords=product"
    },
    {
        "name": "Shopify",
        "link": "https://www.shopify.com/careers/disciplines/product"
    }
    ]
    
    for company in companies_to_scrape:
        url = company["link"]
        clean_url = sanitize_url_for_filename(url)
        setup_logging(clean_url)
        try:
            jobs_found = await get_job_postings(url)
            logger.info(f"Jobs found: {jobs_found}")
        except Exception as e:
            logger.error(f"Error scraping {company['name']}: {str(e)}")
        finally:
            await upload_logs_to_cloud(clean_url)