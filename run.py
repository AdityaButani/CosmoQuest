#!/usr/bin/env python3
"""
CosmosQuest - Learning Adventure Generator
Run script for the Flask application
"""

import os
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    print("🚀 Starting CosmosQuest...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔑 Make sure you have set up your API keys in the .env file")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
