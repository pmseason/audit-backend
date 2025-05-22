from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from loguru import logger
import sys

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.routes import index_router, tasks, audit, instances_router

app.include_router(index_router)
app.include_router(tasks.router)
app.include_router(audit.router)
app.include_router(instances_router)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))  # Default to port 8000 if not specified
    uvicorn.run("src.app:app", host="0.0.0.0", port=port, reload=True) 