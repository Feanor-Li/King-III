#!/usr/bin/env python3
"""
Smart Photo System Main Entry Point
"""

import os
import uvicorn
from dotenv import load_dotenv
from smart_photo_system import create_app

# Load environment variables
load_dotenv()

# Configuration
config = {
    "upload_dir": os.getenv("UPLOAD_DIR", "/tmp/smart_photo_uploads"),
    "output_dir": os.getenv("OUTPUT_DIR", "/tmp/smart_photo_output"),
    "iphone_api_endpoint": os.getenv("IPHONE_API_ENDPOINT", "http://localhost:8080/iphone-control"),
    "capture_api_endpoint": os.getenv("CAPTURE_API_ENDPOINT", "http://localhost:8080/iphone-capture")
}

# Create FastAPI application
app = create_app(config)

if __name__ == "__main__":
    # Development environment settings
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )
