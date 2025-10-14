"""
Search API routes
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas import SearchRequest, SearchResponse, QuickSearchResponse, SortBy
from app.services import scopus_service

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    Search papers dengan filter lengkap dan limit control
    
    - **query**: Keyword pencarian (required)
    - **limit**: Jumlah hasil maksimal (1-1000, default: 25)
    - **year_from**: Filter tahun mulai
    - **year_to**: Filter tahun sampai
    - **document_type**: Tipe dokumen (article, conference, dll)
    - **subject_areas**: Area subjek (computer_science, medicine, dll)
    - **sort_by**: Urutan hasil (citations, date, relevance)
    """
    start_time = datetime.now()
    
    # Use service to search
    papers, full_query, total_available = scopus_service.search_papers(
        query=request.query,
        limit=request.limit,
        year_from=request.year_from,
        year_to=request.year_to,
        document_type=request.document_type.value if request.document_type else None,
        subject_areas=[area.value for area in request.subject_areas] if request.subject_areas else None,
        sort_by=request.sort_by.value
    )
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return SearchResponse(
        total_available=total_available,
        returned_count=len(papers),
        query=full_query,
        papers=papers,
        execution_time=execution_time
    )


@router.get("/quick-search", response_model=QuickSearchResponse)
async def quick_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(25, ge=1, le=1000, description="Result limit"),
    year_from: Optional[int] = Query(None, ge=1900, le=2025),
    year_to: Optional[int] = Query(None, ge=1900, le=2025),
    sort: SortBy = Query(SortBy.citations, description="Sort by")
):
    """
    Quick search endpoint (GET method)
    
    Example: /api/quick-search?q=machine%20learning&limit=50&year_from=2020
    """
    papers, _, _ = scopus_service.search_papers(
        query=q,
        limit=limit,
        year_from=year_from,
        year_to=year_to,
        sort_by=sort.value
    )
    
    return QuickSearchResponse(
        query=q,
        returned_count=len(papers),
        papers=papers
    )


@router.get("/highly-cited")
async def get_highly_cited(
    query: str = Query(..., description="Search query"),
    min_citations: int = Query(100, ge=1, description="Minimum citations"),
    limit: int = Query(50, ge=1, le=500)
):
    """Get highly cited papers (filtered by minimum citations)"""
    papers, _, _ = scopus_service.search_papers(
        query=query,
        limit=limit,
        sort_by="-citedby-count"
    )
    
    # Filter by min citations
    highly_cited = [p for p in papers if p['cited_by'] >= min_citations]
    
    return {
        "query": query,
        "min_citations": min_citations,
        "total_found": len(highly_cited),
        "papers": highly_cited
    }
