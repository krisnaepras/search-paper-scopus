"""
Main FastAPI Application
Clean architecture with modular routing
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response, PlainTextResponse, RedirectResponse
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
    
    # Prepare SEO helpers
    verification_meta_tags = []
    for meta_name, value in [
        ("google-site-verification", settings.google_site_verification),
        ("msvalidate.01", settings.bing_site_verification),
        ("yandex-verification", settings.yandex_site_verification),
    ]:
        if value:
            verification_meta_tags.append(f'<meta name="{meta_name}" content="{value}" />')
    
    def inject_verification_tags(html: str) -> str:
        """Inject verification meta tags before closing head"""
        if not verification_meta_tags:
            return html
        injection = "\n    ".join(verification_meta_tags) + "\n"
        if "</head>" in html:
            return html.replace("</head>", f"    {injection}</head>", 1)
        return html + f"\n{injection}"
    
    def get_index_last_modified() -> str:
        """Return last modified date for sitemap entries"""
        html_path = os.path.join(static_path, "index.html")
        if os.path.exists(html_path):
            return datetime.utcfromtimestamp(os.path.getmtime(html_path)).date().isoformat()
        return datetime.utcnow().date().isoformat()
    
    def build_sitemap_entries(base_url: str, last_modified: str) -> list[dict[str, str]]:
        """Construct sitemap entries"""
        urls = [
            {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0", "lastmod": last_modified},
        ]
        for path in settings.sitemap_extra_paths_list:
            urls.append(
                {
                    "loc": f"{base_url}{path}",
                    "changefreq": "weekly",
                    "priority": "0.7",
                    "lastmod": last_modified,
                }
            )
        return urls
    
    # Canonical host / HTTPS enforcement
    if settings.canonical_hostname or settings.force_https:
        @app.middleware("http")
        async def canonical_redirect_middleware(request: Request, call_next):
            host_header = request.headers.get("host")
            current_host = (host_header or request.url.hostname or "").split(":")[0].lower()
            desired_host = settings.canonical_hostname or current_host
            scheme = request.url.scheme
            redirect_needed = False
            target_scheme = scheme
            
            if settings.canonical_hostname and current_host and current_host != settings.canonical_hostname:
                redirect_needed = True
            
            if settings.force_https and scheme != "https":
                redirect_needed = True
                target_scheme = "https"
            
            if redirect_needed and desired_host:
                netloc = desired_host
                port = request.url.port
                if port and port not in (80, 443):
                    netloc = f"{desired_host}:{port}"
                final_scheme = settings.canonical_scheme or target_scheme
                new_url = request.url.replace(netloc=netloc, scheme=final_scheme)
                return RedirectResponse(str(new_url), status_code=308)
            
            return await call_next(request)
    
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
                return inject_verification_tags(f.read())
        else:
            return inject_verification_tags("""
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>🚀 Scopus Search REST API</h1>
                    <p>API is running successfully!</p>
                    <p>Version: {version}</p>
                    <p>Access the documentation at <a href="/docs">/docs</a></p>
                </body>
            </html>
            """.format(version=settings.app_version))

    @app.get("/sitemap.xml")
    async def sitemap(request: Request):
        """Serve dynamic sitemap with current host"""
        base_url = str(request.base_url).rstrip("/")
        last_modified = get_index_last_modified()
        sitemap_urls = build_sitemap_entries(base_url, last_modified)

        xml_lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<urlset xmlns=\"https://www.sitemaps.org/schemas/sitemap/0.9\">",
        ]

        for entry in sitemap_urls:
            xml_lines.extend(
                [
                    "  <url>",
                    f"    <loc>{entry['loc']}</loc>",
                    f"    <lastmod>{entry['lastmod']}</lastmod>",
                    f"    <changefreq>{entry['changefreq']}</changefreq>",
                    f"    <priority>{entry['priority']}</priority>",
                    "  </url>",
                ]
            )

        xml_lines.append("</urlset>")

        return Response(
            "\n".join(xml_lines),
            media_type="application/xml",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    @app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
    async def robots_txt(request: Request):
        """Expose crawl instructions and sitemap for search engines"""
        base_url = str(request.base_url).rstrip("/")
        rules = [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {base_url}/sitemap.xml",
        ]
        return PlainTextResponse("\n".join(rules), headers={"Cache-Control": "public, max-age=3600"})
    
    @app.middleware("http")
    async def seo_headers_middleware(request: Request, call_next):
        """Append helpful security + SEO headers"""
        response = await call_next(request)
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            response.headers.setdefault("X-Robots-Tag", "index, follow")
            response.headers.setdefault("Cache-Control", "public, max-age=300")
        return response
    
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
