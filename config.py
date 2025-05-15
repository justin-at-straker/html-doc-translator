"""Configuration for the HTML translation service."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Cloud Translation settings
    # pydantic-settings will automatically look for GCP_PROJECT_ID env var
    gcp_project_id: str | None = None 
    # pydantic-settings will look for GCP_LOCATION, defaults to "global" if not found
    gcp_location: str = "global" 
    # Add the missing GOOGLE_APPLICATION_CREDENTIALS field
    # pydantic-settings will look for GOOGLE_APPLICATION_CREDENTIALS
    google_application_credentials: str | None = None 

    # OpenAI Translation settings
    # pydantic-settings will look for OPENAI_API_KEY
    openai_api_key: str | None = None 
    # pydantic-settings will look for OPENAI_MODEL, defaults to "gpt-3.5-turbo"
    openai_model: str = "gpt-3.5-turbo"
    
    # Default translation provider
    # pydantic-settings will look for TRANSLATION_PROVIDER, defaults to "google"
    translation_provider: str = "google"
    
    class Config:
        env_file = ".env"
        # Optional: if you want to ensure your env var names are case-insensitive when reading from actual env
        # (pydantic-settings is already case-insensitive for .env files by default)
        # case_sensitive = False 
        # By default, pydantic-settings allows extra fields in the .env file but ignores them 
        # if they are not in the model. The error implies a stricter mode or a different issue.
        # However, the primary fix is aligning field definitions with pydantic-settings patterns.


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings() 