import os
from pathlib import Path
from pydantic_settings import BaseSettings

class ProductConfig(BaseSettings):

    # Azure Configuration 
    AZURE_API_VERSION: str = "2025-04-01-preview"
    
    # Models
    IMAGE_MODEL: str = "gpt-image-1.5"
    REASONING_MODEL: str = "gpt-5.2"
    
    # Local Output (Fallback)
    OUTPUT_DIR: Path = Path(__file__).parent / "output_product"

    class Config:
        env_file = ".env"
        extra = "ignore"

product_config = ProductConfig()
