"""
Search API routes
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import SearchRequest, SearchResponse, QuickSearchResponse, SortBy
from app.db.database import get_db
from app.db.models import User, ApiKey
from app.core.dependencies import get_current_user
from app.core.security import decrypt_api_key

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_papers(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    
    # Get user's active API key
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=403,
            detail="No active Scopus API key found. Please add an API key first."
        )
    
    # Decrypt API key before use
    decrypted_key = decrypt_api_key(api_key.api_key)
    
    # Create ScopusService instance with user's API key
    from app.services.scopus_service import ScopusService
    user_scopus_service = ScopusService(decrypted_key)
    
    # Use service to search
    try:
        papers, full_query, total_available = user_scopus_service.search_papers(
            query=request.query,
            limit=request.limit,
            year_from=request.year_from,
            year_to=request.year_to,
            document_type=request.document_type.value if request.document_type else None,
            subject_areas=[area.value for area in request.subject_areas] if request.subject_areas else None,
            sort_by=request.sort_by.value,
            page=request.page,
            use_cache=False  # Disable caching to avoid Redis issues
        )
    except HTTPException:
        # Re-raise HTTPException as is
        raise
    except Exception as e:
        # Catch any other errors from Scopus API
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
    
    execution_time = (datetime.now() - start_time).total_seconds()

    total_pages = max(1, math.ceil(total_available / request.limit)) if request.limit else 1
    current_page = min(max(1, request.page), total_pages)

    if current_page != request.page and total_available > 0:
        papers, full_query, total_available = user_scopus_service.search_papers(
            query=request.query,
            limit=request.limit,
            year_from=request.year_from,
            year_to=request.year_to,
            document_type=request.document_type.value if request.document_type else None,
            subject_areas=[area.value for area in request.subject_areas] if request.subject_areas else None,
            sort_by=request.sort_by.value,
            page=current_page,
            use_cache=False
        )
        total_pages = max(1, math.ceil(total_available / request.limit)) if request.limit else 1
    
    return SearchResponse(
        total_available=total_available,
        returned_count=len(papers),
        page=current_page,
        per_page=request.limit,
        total_pages=total_pages,
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
    sort: SortBy = Query(SortBy.citations, description="Sort by"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick search endpoint (GET method) - Requires authentication
    
    Example: /api/quick-search?q=machine%20learning&limit=50&year_from=2020
    """
    # Get user's API key
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=403, detail="No active Scopus API key found")
    
    decrypted_key = decrypt_api_key(api_key.api_key)
    
    from app.services.scopus_service import ScopusService
    user_scopus_service = ScopusService(decrypted_key)
    
    papers, _, _ = user_scopus_service.search_papers(
        query=q,
        limit=limit,
        year_from=year_from,
        year_to=year_to,
        sort_by=sort.value,
        use_cache=False
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
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get highly cited papers (filtered by minimum citations) - Requires authentication"""
    # Get user's API key
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=403, detail="No active Scopus API key found")
    
    decrypted_key = decrypt_api_key(api_key.api_key)
    
    from app.services.scopus_service import ScopusService
    user_scopus_service = ScopusService(decrypted_key)
    
    papers, _, _ = user_scopus_service.search_papers(
        query=query,
        limit=limit,
        sort_by="-citedby-count",
        use_cache=False
    )
    
    # Filter by min citations
    highly_cited = [p for p in papers if p['cited_by'] >= min_citations]
    
    return {
        "query": query,
        "min_citations": min_citations,
        "total_found": len(highly_cited),
        "papers": highly_cited
    }
