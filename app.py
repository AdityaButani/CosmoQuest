import os
import logging
from flask import Flask, session
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cosmosquest-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure session settings - use server-side storage for large quest data
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_PERMANENT'] = True

# In-memory storage for quest data (in production, use Redis or database)
quest_data_cache = {}

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    # Disable debug mode for testing to prevent auto-restarts
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
