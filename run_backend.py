#!/usr/bin/env python3
"""
Run the FastAPI backend server
"""
import uvicorn
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.api_controller import app

if __name__ == "__main__":
    # Only watch backend directory for changes to avoid reloading on extension changes
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        reload_dirs=[backend_dir]
    )

