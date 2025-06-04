async def find_open_roles(url: str):
    return [
        {
            "id": 1,
            "title": "Senior Software Engineer",
            "company": "TechCorp Inc",
            "location": "San Francisco, CA",
            "description": "Looking for an experienced software engineer to join our growing team. Must have 5+ years experience with Python and cloud technologies.",
            "task": 1,
            "url": f"{url}/job/senior-software-engineer",
            "other": "Full-time, Remote optional"
        },
        {
            "id": 2, 
            "title": "Product Manager",
            "company": "TechCorp Inc",
            "location": "New York, NY",
            "description": "Seeking a product manager to lead our flagship product initiatives. Must have experience with agile methodologies and technical products.",
            "task": 1,
            "url": f"{url}/job/product-manager",
            "other": "Full-time, On-site"
        },
        {
            "id": 3,
            "title": "UX Designer",
            "company": "TechCorp Inc", 
            "location": "Austin, TX",
            "description": "Join our design team to create beautiful and intuitive user experiences. Looking for someone with strong portfolio and 3+ years experience.",
            "task": 1,
            "url": f"{url}/job/ux-designer",
            "other": "Full-time, Hybrid"
        }
    ]