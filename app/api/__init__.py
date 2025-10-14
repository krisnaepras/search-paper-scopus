"""
API routes module - All API endpoints
"""

from app.api import search, stats, export, author, download, health, auth, apikeys, wishlist

__all__ = ["search", "stats", "export", "author", "download", "health", "auth", "apikeys", "wishlist"]
