"""
Configuration module using Pydantic Settings
Supports environment variables and .env files
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration (Default - users can override with their own)
    scopus_api_key: str = "73439d14c6dc73b3a06756cbc9de5a4a"
    scopus_base_url: str = "https://api.elsevier.com/content/search/scopus"
    
    # Server Configuration
    app_name: str = "Scopus Search API"
    app_version: str = "3.0.0"
    app_description: str = "REST API untuk searching paper di Scopus dengan authentication dan wishlist"
    debug: bool = False
    
    # Database Configuration (PostgreSQL from Heroku)
    database_url: str = "postgresql://user:password@localhost:5432/scopus_db"
    
    @property
    def database_url_fixed(self) -> str:
        """Fix database URL - Heroku uses postgres:// but SQLAlchemy needs postgresql://"""
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql://", 1)
        return self.database_url
    
    # Redis Configuration (from Heroku)
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600  # 1 hour
    
    # Security Configuration
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    encryption_key: str = secrets.token_urlsafe(32)  # For encrypting API keys
    
    # CORS Settings
    cors_origins: str = "*"  # Changed to string, can be comma-separated
    cors_credentials: bool = True
    cors_methods: str = "*"
    cors_headers: str = "*"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # API Limits
    max_results_per_page: int = 25
    max_total_results: int = 1000
    default_limit: int = 25
    request_timeout: int = 30
    
    # Static Files
    static_dir: str = "static"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Create global settings instance
settings = Settings()
