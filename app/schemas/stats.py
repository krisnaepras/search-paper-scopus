"""
Statistics response models
"""

from pydantic import BaseModel, Field
from typing import Dict


class StatsResponse(BaseModel):
    """Statistical analysis of search results"""
    total_papers: int = Field(..., description="Total number of papers")
    total_citations: int = Field(..., description="Sum of all citations")
    avg_citations: float = Field(..., description="Average citations per paper")
    median_citations: float = Field(..., description="Median citations")
    max_citations: int = Field(..., description="Maximum citations")
    min_citations: int = Field(..., description="Minimum citations")
    year_range: str = Field(..., description="Year range of papers")
    papers_per_year: Dict[str, int] = Field(..., description="Distribution by year")
    top_journals: Dict[str, int] = Field(..., description="Top 10 journals/conferences")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_papers": 50,
                "total_citations": 2500,
                "avg_citations": 50.0,
                "median_citations": 35.0,
                "max_citations": 250,
                "min_citations": 0,
                "year_range": "2020 - 2024",
                "papers_per_year": {"2020": 10, "2021": 15, "2022": 12, "2023": 8, "2024": 5},
                "top_journals": {"Nature": 5, "Science": 4}
            }
        }
