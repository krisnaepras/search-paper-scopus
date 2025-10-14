"""
Download and DOI resolution API routes
"""

from fastapi import APIRouter, Path, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/download")
async def download_paper(
    scopus_id: str = Query(..., description="Scopus ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Download paper via Sci-Hub redirect
    """
    if not scopus_id or scopus_id == 'N/A':
        raise HTTPException(status_code=404, detail="Scopus ID not available")
    
    # Redirect to Sci-Hub (try multiple mirrors)
    scihub_url = f"https://sci-hub.se/{scopus_id}"
    
    return RedirectResponse(url=scihub_url)


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
async def get_download_info(
    eid: str = Path(..., description="Scopus EID"),
    current_user: User = Depends(get_current_user)
):
    """
    Get download information for a paper by EID
    Returns multiple download options
    """
    if eid == 'N/A' or not eid:
        raise HTTPException(status_code=404, detail="EID not available")
    
    # For now, return basic download info without fetching from Scopus
    # (since scopus_service singleton was removed)
    doi = 'N/A'
    title = eid
    
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
    
    return download_options
