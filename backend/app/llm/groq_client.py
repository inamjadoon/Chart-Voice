import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client using the API key from environment variables.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please add it to your backend/.env file.")
    
    return Groq(api_key=api_key)