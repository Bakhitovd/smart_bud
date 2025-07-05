#!/usr/bin/env python3
"""
Smart Budget Companion - Backend Server
Run this script to start the FastAPI server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting Smart Budget Companion Backend...")
    print("📊 Make sure to set your OPENAI_API_KEY in backend/.env")
    print("🌐 Frontend will be available at: http://localhost:8000 (after opening frontend/index.html)")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("⚠️  WARNING: OpenAI API key not set! Please update backend/.env with your API key.")
        print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
