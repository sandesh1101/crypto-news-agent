import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)  # Add override=True to ensure latest values are loaded

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Output configuration
NEWS_OUTPUT_DIR = os.getenv("NEWS_OUTPUT_DIR", "news_output")  # Default: 'news_output' directory in project root

# Debug output
print("Current working directory:", os.getcwd())
print("Environment file exists:", os.path.exists('.env'))
print("News API Key loaded:", 'Yes' if NEWS_API_KEY else 'No')

# Validate required environment variables
if not OPENAI_API_KEY or not NEWS_API_KEY:
    raise ValueError("Missing required environment variables. Please check your .env file.")
