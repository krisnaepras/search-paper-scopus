"""
Main FastAPI Application
Clean architecture with modular routing
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response
import os
from datetime import datetime

from app.core.config import settings
from app.api import search, stats, export, author, download, health, auth, apikeys, wishlist, debug
from app.db import init_db


def create_application() -> FastAPI:
    """
    Application factory pattern
    Creates and configures FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        # docs_url="/docs",
        # redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_credentials,
        allow_methods=[settings.cors_methods] if settings.cors_methods == "*" else settings.cors_methods.split(","),
        allow_headers=[settings.cors_headers] if settings.cors_headers == "*" else settings.cors_headers.split(","),
    )
    
    # Mount static files
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.static_dir)
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Register routers
    app.include_router(health.router)
    app.include_router(auth.router)  # Authentication
    app.include_router(apikeys.router)  # API Key Management
    app.include_router(wishlist.router)  # Wishlist
    app.include_router(debug.router)  # Debug endpoints
    app.include_router(search.router)
    app.include_router(stats.router)
    app.include_router(export.router)
    app.include_router(author.router)
    app.include_router(download.router)
    
    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize database tables on startup"""
        init_db()
    
    # Root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve web interface"""
        html_path = os.path.join(static_path, "index.html")
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return """
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>🚀 Scopus Search REST API</h1>
                    <p>API is running successfully!</p>
                    <p>Version: {version}</p>
                    <p>Access the documentation at <a href="/docs">/docs</a></p>
                </body>
            </html>
            """.format(version=settings.app_version)

    @app.get("/sitemap.xml")
    async def sitemap(request: Request):
        """Serve dynamic sitemap with current host"""
        base_url = str(request.base_url).rstrip("/")
        last_modified = datetime.utcnow().date().isoformat()
        sitemap_urls = [
            {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},
            # {"loc": f"{base_url}/docs", "changefreq": "weekly", "priority": "0.7"},
            # {"loc": f"{base_url}/redoc", "changefreq": "weekly", "priority": "0.6"},
        ]

        xml_lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<urlset xmlns=\"https://www.sitemaps.org/schemas/sitemap/0.9\">",
        ]

        for entry in sitemap_urls:
            xml_lines.extend(
                [
                    "  <url>",
                    f"    <loc>{entry['loc']}</loc>",
                    f"    <lastmod>{last_modified}</lastmod>",
                    f"    <changefreq>{entry['changefreq']}</changefreq>",
                    f"    <priority>{entry['priority']}</priority>",
                    "  </url>",
                ]
            )

        xml_lines.append("</urlset>")

        return Response("\n".join(xml_lines), media_type="application/xml")
    
    # Global exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": str(exc) if settings.debug else "Internal server error",
                "status_code": 500
            }
        )
    
    return app


# Create app instance
app = create_application()
