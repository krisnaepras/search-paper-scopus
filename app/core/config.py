"""
Configuration module using Pydantic Settings
Supports environment variables and .env files
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets
from urllib.parse import quote


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
    
    # SEO / Console configuration
    canonical_host: Optional[str] = None  # e.g. https://example.com
    canonical_scheme: Optional[str] = None  # override scheme for redirects if needed
    force_https: bool = False
    google_site_verification: Optional[str] = None
    bing_site_verification: Optional[str] = None
    yandex_site_verification: Optional[str] = None
    sitemap_extra_paths: str = "/docs,/redoc"
    
    # Download / Mirror configuration
    scihub_mirrors: str = (
        "https://sci-hub.se,"
        "https://sci-hub.st,"
        "https://sci-hub.ru,"
        "https://sci-hub.is,"
        "https://sci-hub.ren,"
        "https://sci-hub.hkvisa.net,"
        "https://sci-hub.it.nrw,"
        "https://sci-hub.wf"
    )
    
    @property
    def canonical_hostname(self) -> Optional[str]:
        """Return sanitized canonical hostname for redirect enforcement"""
        if not self.canonical_host:
            return None
        host = self.canonical_host.lower().strip()
        if host.startswith("https://"):
            host = host[len("https://") :]
        elif host.startswith("http://"):
            host = host[len("http://") :]
        return host.split("/")[0]
    
    @property
    def sitemap_extra_paths_list(self) -> list[str]:
        """Return list of extra sitemap paths"""
        if not self.sitemap_extra_paths:
            return []
        paths: list[str] = []
        for raw in self.sitemap_extra_paths.split(","):
            path = raw.strip()
            if not path:
                continue
            if not path.startswith("/"):
                path = f"/{path}"
            paths.append(path)
        return paths
    
    @property
    def scihub_mirror_list(self) -> list[str]:
        """Return list of sanitized Sci-Hub mirrors"""
        mirrors: list[str] = []
        for raw in self.scihub_mirrors.split(","):
            mirror = raw.strip()
            if not mirror:
                continue
            if not mirror.startswith(("http://", "https://")):
                mirror = f"https://{mirror}"
            mirror = mirror.rstrip("/")
            if mirror:
                mirrors.append(mirror)
        return mirrors or ["https://sci-hub.se"]
    
    def build_scihub_urls(self, identifier: str) -> list[str]:
        """Build Sci-Hub URLs for a cleaned DOI/identifier"""
        if not identifier:
            return []
        clean_identifier = (
            identifier.strip()
            .replace("https://doi.org/", "")
            .replace("http://doi.org/", "")
            .replace("https://dx.doi.org/", "")
            .replace("http://dx.doi.org/", "")
            .replace("doi:", "")
            .replace("DOI:", "")
        ).lstrip("/")
        if not clean_identifier:
            return []
        encoded_identifier = quote(clean_identifier, safe="/:;()@._-")
        return [f"{mirror}/{encoded_identifier}" for mirror in self.scihub_mirror_list]
    
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
