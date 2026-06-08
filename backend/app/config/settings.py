"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Ocean.io API - Similar Company Discovery
    OCEAN_API_KEY: Optional[str] = None
    OCEAN_API_URL: str = "https://api.ocean.io/v1"

    # Prospeo API - Decision Maker Discovery
    PROSPEO_API_KEY: Optional[str] = None
    PROSPEO_API_URL: str = "https://api.prospeo.io/v1"

    # Eazyreach API - Email Resolution
    EAZYREACH_API_KEY: Optional[str] = None
    EAZYREACH_API_URL: str = "https://api.eazyreach.io/v1"

    # Brevo (Sendinblue) API - Email Sending
    BREVO_API_KEY: Optional[str] = None
    BREVO_API_URL: str = "https://api.brevo.com/v3"
    BREVO_SENDER_EMAIL: str = "outreach@yourdomain.com"
    BREVO_SENDER_NAME: str = "Outreach Team"

    # Pipeline Settings
    MAX_SIMILAR_COMPANIES: int = 20
    MAX_CONTACTS_PER_COMPANY: int = 5
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    # App Settings
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
