"""
Search request and response models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.enums import DocumentType, SubjectArea, SortBy
from app.schemas.paper import PaperResponse


class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(..., description="Search query (e.g., 'machine learning')", min_length=1)
    limit: int = Field(25, ge=1, le=1000, description="Maximum number of results (1-1000)")
    year_from: Optional[int] = Field(None, ge=1900, le=2025, description="Start year")
    year_to: Optional[int] = Field(None, ge=1900, le=2025, description="End year")
    document_type: Optional[DocumentType] = Field(None, description="Document type filter")
    subject_areas: Optional[List[SubjectArea]] = Field(None, description="Subject area filters")
    sort_by: SortBy = Field(SortBy.citations, description="Sort results by")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning",
                "limit": 50,
                "year_from": 2020,
                "year_to": 2024,
                "document_type": "ar",
                "subject_areas": ["COMP"],
                "sort_by": "citations"
            }
        }


class SearchResponse(BaseModel):
    """Search response with results"""
    total_available: int = Field(..., description="Total papers available in Scopus")
    returned_count: int = Field(..., description="Number of papers returned")
    query: str = Field(..., description="Actual query used")
    papers: List[PaperResponse] = Field(..., description="List of papers")
    execution_time: float = Field(..., description="Query execution time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_available": 5420,
                "returned_count": 50,
                "query": "machine learning AND PUBYEAR > 2019 AND PUBYEAR < 2025",
                "papers": [],
                "execution_time": 2.45
            }
        }


class QuickSearchResponse(BaseModel):
    """Quick search response (simplified)"""
    query: str = Field(..., description="Search query")
    returned_count: int = Field(..., description="Number of papers returned")
    papers: List[PaperResponse] = Field(..., description="List of papers")
