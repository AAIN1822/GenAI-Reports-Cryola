import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- CREDENTIALS - Need to be enabled in production  ---
    
    """
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "") 
    AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
    AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    """
       
    # Models
    GPT_MODEL = "gpt-5" 
    CRITIC_GPT_MODEL =  "gpt-5.2"
    GPT_API_VERSION = "2025-01-01-preview"
    IMAGE_MODEL = "gpt-image-1.5" 
    IMAGE_API_VERSION = "2025-04-01-preview"
    
    # Logic Thresholds
    OUTPUT_DIR = Path("outputs") # Local fallback