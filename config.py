"""Configuration for the HTML translation service."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Cloud Translation settings
    gcp_project_id: str | None = None 
    gcp_location: str = "global"
    google_application_credentials: str | None = None 

    # OpenAI Translation settings
    openai_api_key: str | None = None 
    openai_model: str = "gpt-3.5-turbo"
    
    # Default translation provider
    translation_provider: str = "google"
    
    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings() 