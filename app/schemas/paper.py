"""
Paper response models
"""

from pydantic import BaseModel, Field


class PaperResponse(BaseModel):
    """Individual paper response"""
    title: str = Field(..., description="Paper title")
    authors: str = Field(..., description="Authors names")
    year: str = Field(..., description="Publication year")
    publication: str = Field(..., description="Journal/Conference name")
    cited_by: int = Field(..., description="Citation count")
    doi: str = Field(..., description="Digital Object Identifier")
    document_type: str = Field(..., description="Document type")
    source_type: str = Field(..., description="Source type")
    affiliation: str = Field(..., description="Institution/University")
    eid: str = Field(..., description="Scopus EID")
    scopus_url: str = Field(..., description="Scopus record URL")
    open_access: bool = Field(..., description="Is open access")
    pdf_url: str = Field(..., description="PDF download URL if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning in Healthcare",
                "authors": "Smith J., Doe A.",
                "year": "2023",
                "publication": "Nature Medicine",
                "cited_by": 150,
                "doi": "10.1038/s41591-023-xxxxx",
                "document_type": "Article",
                "source_type": "Journal",
                "affiliation": "Stanford University",
                "eid": "2-s2.0-85123456789",
                "scopus_url": "https://www.scopus.com/record/display.uri?eid=...",
                "open_access": True,
                "pdf_url": "https://..."
            }
        }
