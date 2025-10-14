#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus Search REST API - Entry Point
Run this file to start the server
"""

import uvicorn
from app.core.config import settings


def main():
    """Main entry point for the application"""
    print("=" * 80)
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print("=" * 80)
    print("\n📍 Endpoints:")
    print("   • Web Interface: http://localhost:8000")
    print("   • API Docs (Swagger): http://localhost:8000/docs")
    print("   • API Docs (ReDoc): http://localhost:8000/redoc")
    print("   • API Info: http://localhost:8000/api")
    print("   • Health Check: http://localhost:8000/health")
    print("\n🔥 Server running on: http://localhost:8000")
    print("=" * 80)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
