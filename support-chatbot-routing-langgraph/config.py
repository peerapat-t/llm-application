# config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file at the project root
load_dotenv()

def get_openai_api_key():
    """
    Retrieves the OpenAI API key from environment variables.
    Raises an error if the key is not found.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ValueError("OPENAI_API_KEY not found or not set in .env file.")
    return api_key

# For direct access if needed, though get_openai_api_key() is safer
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def setup_environment():
    """Sets the OpenAI API key as an environment variable for other modules."""
    os.environ["OPENAI_API_KEY"] = get_openai_api_key()