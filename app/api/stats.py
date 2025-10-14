"""
Statistics API routes
"""

from fastapi import APIRouter, HTTPException
import pandas as pd

from app.schemas import SearchRequest, StatsResponse
from app.services import scopus_service

router = APIRouter(prefix="/api", tags=["statistics"])


@router.post("/stats", response_model=StatsResponse)
async def get_statistics(request: SearchRequest):
    """
    Get statistical analysis dari hasil search
    
    Provides comprehensive statistics including:
    - Citation metrics (total, average, median, min, max)
    - Year distribution
    - Top journals/conferences
    """
    # Use service to search
    papers, _, _ = scopus_service.search_papers(
        query=request.query,
        limit=request.limit,
        year_from=request.year_from,
        year_to=request.year_to,
        document_type=request.document_type.value if request.document_type else None,
        subject_areas=[area.value for area in request.subject_areas] if request.subject_areas else None,
        sort_by=request.sort_by.value
    )
    
    if not papers:
        raise HTTPException(status_code=404, detail="No papers found")
    
    # Create DataFrame for analysis
    df = pd.DataFrame(papers)
    
    # Calculate statistics
    citations = df['cited_by'].tolist()
    years = df['year'].value_counts().to_dict()
    journals = df['publication'].value_counts().head(10).to_dict()
    
    return StatsResponse(
        total_papers=len(papers),
        total_citations=sum(citations),
        avg_citations=sum(citations) / len(citations) if citations else 0,
        median_citations=sorted(citations)[len(citations)//2] if citations else 0,
        max_citations=max(citations) if citations else 0,
        min_citations=min(citations) if citations else 0,
        year_range=f"{df['year'].min()} - {df['year'].max()}",
        papers_per_year=years,
        top_journals=journals
    )
