"""
Download and DOI resolution API routes
"""

from fastapi import APIRouter, Path, HTTPException
import requests

from app.core.config import settings
from app.services import scopus_service

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/pdf-link/{doi:path}")
async def get_pdf_link(doi: str = Path(..., description="DOI of the paper")):
    """
    Get PDF download link for a paper by DOI
    Redirects to Sci-Hub or DOI resolver
    """
    if doi == 'N/A' or not doi:
        raise HTTPException(status_code=404, detail="DOI not available")
    
    # Clean DOI
    doi_clean = doi.replace('http://', '').replace('https://', '').replace('doi.org/', '')
    
    return {
        "doi": doi_clean,
        "doi_url": f"https://doi.org/{doi_clean}",
        "scihub_urls": [
            f"https://sci-hub.se/{doi_clean}",
            f"https://sci-hub.st/{doi_clean}",
            f"https://sci-hub.ru/{doi_clean}"
        ],
        "note": "Sci-Hub provides free access to academic papers. Use at your own discretion and respect copyright laws."
    }


@router.get("/download-info/{eid}")
async def get_download_info(eid: str = Path(..., description="Scopus EID")):
    """
    Get download information for a paper by EID
    Returns multiple download options
    """
    if eid == 'N/A' or not eid:
        raise HTTPException(status_code=404, detail="EID not available")
    
    # Get paper details
    paper = scopus_service.get_paper_by_eid(eid)
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    doi = paper.get('doi', 'N/A')
    title = paper.get('title', 'N/A')
    
    download_options = {
        "eid": eid,
        "title": title,
        "doi": doi,
        "scopus_url": f"https://www.scopus.com/record/display.uri?eid={eid}&origin=resultslist",
        "download_methods": []
    }
    
    if doi != 'N/A':
        doi_clean = doi.replace('http://', '').replace('https://', '').replace('doi.org/', '')
        download_options["download_methods"].extend([
            {
                "method": "Official Publisher",
                "url": f"https://doi.org/{doi_clean}",
                "type": "official",
                "note": "May require subscription or payment"
            },
            {
                "method": "Sci-Hub (Mirror 1)",
                "url": f"https://sci-hub.se/{doi_clean}",
                "type": "scihub",
                "note": "Free access - check your local laws"
            },
            {
                "method": "Sci-Hub (Mirror 2)",
                "url": f"https://sci-hub.st/{doi_clean}",
                "type": "scihub",
                "note": "Free access - check your local laws"
            },
            {
                "method": "Google Scholar",
                "url": f"https://scholar.google.com/scholar?q={title.replace(' ', '+')}",
                "type": "search",
                "note": "May find free PDF versions"
            }
        ])
    
    # Check for open access
    if paper.get('open_access'):
        download_options["open_access"] = True
        download_options["note"] = "This paper is Open Access - free download should be available"
    
    return download_options
