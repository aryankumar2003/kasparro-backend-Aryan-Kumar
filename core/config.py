import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Data Ingestion System"
    API_V1_STR: str = "/api/v1"
    API_KEY: str = Field(..., description="API Key for authentication")
    
    # Database
    DATABASE_URL: str = Field(..., description="Database connection string")
    
    # Ingestion Settings
    COINPAPRIKA_API_URL: str = "https://api.coinpaprika.com/v1"
    COINPAPRIKA_API_KEY: str = Field(default="", description="Optional API Key for CoinPaprika")
    COINGECKO_API_KEY: str = Field(default="", description="Optional API Key for CoinGecko")
    COIN_IDS: list[str] = Field(default=["btc-bitcoin"], description="List of Coin IDs to fetch")
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    
    # Extra
    RSS_FEEDS: list[str] = []
    API_SOURCES: list[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
