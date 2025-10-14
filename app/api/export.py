"""
Export API routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import io
from datetime import datetime

from app.schemas import SearchRequest, ExportFormat
from app.services import scopus_service

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export/{format}")
async def export_results(
    format: ExportFormat,
    request: SearchRequest
):
    """
    Export hasil search ke berbagai format
    
    - **json**: JSON file
    - **csv**: CSV file
    - **excel**: Excel file (.xlsx)
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
    
    df = pd.DataFrame(papers)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == ExportFormat.json:
        # Export as JSON
        return JSONResponse(content=papers)
    
    elif format == ExportFormat.csv:
        # Export as CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scopus_results_{timestamp}.csv"
            }
        )
    
    elif format == ExportFormat.excel:
        # Export as Excel
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=scopus_results_{timestamp}.xlsx"
            }
        )
