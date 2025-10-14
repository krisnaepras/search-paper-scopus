"""
Health check and info API routes
"""

from fastapi import APIRouter
from datetime import datetime

from app.core.config import settings
from app.services import scopus_service

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test API connection
        result = scopus_service.search("test", count=1)
        api_status = "healthy" if result else "unhealthy"
    except:
        api_status = "unhealthy"
    
    return {
        "status": "healthy",
        "scopus_api": api_status,
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version
    }


@router.get("/api")
async def api_info():
    """API info endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "endpoints": {
            "web_interface": "/",
            "search": "/api/search",
            "quick_search": "/api/quick-search",
            "stats": "/api/stats",
            "export": "/api/export/{format}",
            "author_search": "/api/author/{name}",
            "affiliation_search": "/api/affiliation/{institution}",
            "highly_cited": "/api/highly-cited",
            "pdf_link": "/api/pdf-link/{doi}",
            "download_info": "/api/download-info/{eid}",
            "health": "/health",
            "docs": "/docs"
        },
        "status": "running"
    }
