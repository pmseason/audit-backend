import sys
from pathlib import Path
from loguru import logger
import os
from datetime import datetime
from src.services.cloud_storage import upload_file_to_bucket

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging(run_id: str = None):
    """
    Configure logging with both console and file output.
    
    Args:
        run_id: Optional identifier for the current run. If not provided, will use timestamp.
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Generate run identifier
    if not run_id:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create run-specific log directory
    run_log_dir = LOGS_DIR / run_id
    run_log_dir.mkdir(exist_ok=True)
    
    # Add file handler for all logs
    logger.add(
        run_log_dir / "all.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        mode="w"
    )
    
    # Add file handler for errors only
    logger.add(
        run_log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        mode="w"
    )
    
    return run_id

async def upload_logs_to_cloud(run_id: str):
    """
    Upload log files to cloud storage.
    
    Args:
        run_id: The identifier for the run whose logs should be uploaded
    """
    run_log_dir = LOGS_DIR / run_id
    
    if not run_log_dir.exists():
        logger.warning(f"No logs found for run {run_id}")
        return
    
    for log_file in run_log_dir.glob("*.{log,txt}"):
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Upload to cloud storage
            cloud_path = f"logs/{run_id}/{log_file.name}"
            await upload_file_to_bucket(
                file_path=cloud_path,
                content=content,
                content_type="text/plain"
            )
            logger.info(f"Uploaded {log_file.name} to cloud storage")
        except Exception as e:
            logger.error(f"Failed to upload {log_file.name}: {str(e)}")
    
    # Delete the run log directory after successful upload
    try:
        import shutil
        shutil.rmtree(run_log_dir)
        logger.info(f"Deleted local log directory for run {run_id}")
    except Exception as e:
        logger.error(f"Failed to delete local log directory: {str(e)}") 