from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.load_keyvault import load_keyvault_secrets

class Settings(BaseSettings):
    # cosmos db
    COSMOS_ENDPOINT: str
    COSMOS_KEY: str

    # email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    # microsoft SSO
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_TENANT_ID: str

    # security settings
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_HOURS: int

    # azure blob storage
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str
    AZURE_BLOB_CONTAINER_NAME: str

    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY : str
    
    THEME_SCORE_THRESHOLD: int
    THEME_REFINE_SCORE_THRESHOLD: int
    THEME_MAX_RETRY_ATTEMPTS: int

    GRAPHIC_SCORE_THRESHOLD: int
    GRAPHIC_REFINE_SCORE_THRESHOLD: int
    GRAPHIC_MAX_RETRY_ATTEMPTS: int
    GRAPHIC_REFINE_MAX_RETRY_ATTEMPTS: int

    PRODUCT_SCORE_THRESHOLD: int
    PRODUCT_REFINE_SCORE_THRESHOLD: int
    PRODUCT_MAX_RETRY_ATTEMPTS: int
    PRODUCT_REFINE_MAX_RETRY_ATTEMPTS:int

    MULTI_ANGLE_MAX_RETRY: int
    MULTI_ANGLE_L2R_VIEW_THRESHOLD: int
    MULTI_ANGLE_STRAIGHT_VIEW_THRESHOLD: int

    AZURE_KEYVAULT_NAME: str
    MAX_IMAGE_SIZE_MB: int
    MAX_IMAGE_DIMENSION: int
    
    DAM_BASE_URL: str
    DAM_AUTH_KEY: str
    
    model_config = SettingsConfigDict(extra="ignore")

def _settings():
    load_keyvault_secrets()   
    return Settings()

class _SettingsProxy:
    def __getattr__(self, name):
        return getattr(_settings(), name)

settings = _SettingsProxy()