from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from loguru import logger
import sys
from src.utils.logging_config import setup_logging

# Configure logging
# run_id = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Create FastAPI app
app = FastAPI(
    title="Audit Backend API",
    description="Backend API for Audit System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://audit.apmseason.com"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.routes import index_router, tasks, audit, instances_router, scrape

app.include_router(index_router)
app.include_router(tasks.router)
app.include_router(audit.router)
app.include_router(instances_router)
app.include_router(scrape.router)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))  # Default to port 8000 if not specified
    hot_reload = os.getenv("HOT_RELOAD", "false").lower() == "true"
    uvicorn.run("src.app:app", host="0.0.0.0", port=port, reload=hot_reload) 