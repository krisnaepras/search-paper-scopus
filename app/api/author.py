"""
Author and Affiliation API routes
"""

from fastapi import APIRouter, Path, Query, HTTPException

from app.services import scopus_service

router = APIRouter(prefix="/api", tags=["author"])


@router.get("/author/{author_name}")
async def search_by_author(
    author_name: str = Path(..., description="Author name"),
    limit: int = Query(25, ge=1, le=100, description="Result limit")
):
    """Search papers by author name"""
    papers = scopus_service.search_by_author(author_name, limit)
    
    return {
        "author": author_name,
        "total_papers": len(papers),
        "papers": papers
    }


@router.get("/affiliation/{institution}")
async def search_by_affiliation(
    institution: str = Path(..., description="Institution/University name"),
    limit: int = Query(25, ge=1, le=100, description="Result limit")
):
    """Search papers by institution/affiliation"""
    papers = scopus_service.search_by_affiliation(institution, limit)
    
    return {
        "institution": institution,
        "total_papers": len(papers),
        "papers": papers
    }
