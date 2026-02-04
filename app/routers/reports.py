"""
Reports Router - Endpoints for PDF report generation and download
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])

# Define the reports directory
REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "reports", 
    "artist_reports"
)

# Ensure the directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)


class GenerateReportRequest(BaseModel):
    artist_name: str
    period: Optional[str] = "Q4 2025"
    include_medialand: Optional[bool] = False


@router.post("/generate")
async def generate_artist_report(request: GenerateReportRequest):
    """
    Generate a PDF report for an artist
    
    Parameters:
    - artist_name: Name of the artist
    - period: Reporting period (default: "Q4 2025")
    - include_medialand: Include Medialand data (default: False)
    
    Returns:
    - success: Whether generation was successful
    - artist_name: Exact artist name from database
    - pdf_filename: Name of generated PDF file
    - pdf_url: URL to download the PDF
    - summary: Brief summary of the report
    """
    logger.info(f"📊 Generating report for artist: {request.artist_name}")
    
    try:
        from app.services.analytics_service import AnalyticsService
        from app.utils.artist_report_generator import ArtistReportGenerator
        
        # Initialize services
        analytics = AnalyticsService()
        generator = ArtistReportGenerator(analytics)
        
        # Generate report
        result = generator.generate_report(
            artist_name=request.artist_name,
            period=request.period,
            include_medialand=request.include_medialand
        )
        
        if result['success']:
            # Add download URL
            result['pdf_url'] = f"/reports/download/{result['pdf_filename']}"
            
            logger.info(f"✅ Report generated: {result['pdf_filename']}")
            
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "artist_name": result['artist_name'],
                    "pdf_filename": result['pdf_filename'],
                    "pdf_path": result['pdf_path'],
                    "pdf_url": result['pdf_url'],
                    "summary": result['summary'],
                    "message": f"✅ PDF-отчет успешно создан для артиста {result['artist_name']}"
                }
            )
        else:
            logger.error(f"❌ Report generation failed: {result['error']}")
            raise HTTPException(
                status_code=404,
                detail=result['error']
            )
            
    except Exception as e:
        logger.error(f"❌ Error generating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download a PDF report by filename
    
    Parameters:
    - filename: Name of the PDF file
    
    Returns:
    - PDF file for download
    """
    # Security check
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    if not filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be downloaded"
        )
    
    file_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report '{filename}' not found"
        )
    
    logger.info(f"📥 Downloading report: {filename}")
    
    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/list")
async def list_reports():
    """
    List all generated PDF reports
    
    Returns:
    - reports: List of available reports with metadata
    - total_count: Total number of reports
    - total_size_mb: Total size of all reports
    """
    try:
        reports = []
        total_size = 0
        
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith('.pdf'):
                file_path = os.path.join(REPORTS_DIR, filename)
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                from datetime import datetime
                total_size += file_size
                
                # Parse artist name from filename
                # Format: Artist_Name_Report_20260204_173424.pdf
                parts = filename.replace('.pdf', '').split('_Report_')
                artist_name = parts[0].replace('_', ' ') if parts else 'Unknown'
                
                reports.append({
                    "filename": filename,
                    "artist_name": artist_name,
                    "download_url": f"/reports/download/{filename}",
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(modified_time).isoformat()
                })
        
        # Sort by created time (newest first)
        reports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "success": True,
            "reports": reports,
            "total_count": len(reports),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reports: {str(e)}"
        )


@router.delete("/delete/{filename}")
async def delete_report(filename: str):
    """
    Delete a PDF report
    
    Parameters:
    - filename: Name of the PDF file to delete
    
    Returns:
    - success: Whether deletion was successful
    """
    # Security check
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    if not filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be deleted"
        )
    
    file_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report '{filename}' not found"
        )
    
    try:
        os.remove(file_path)
        logger.info(f"🗑️  Deleted report: {filename}")
        
        return {
            "success": True,
            "message": f"Report '{filename}' deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting report: {str(e)}"
        )


@router.get("/info/{filename}")
async def get_report_info(filename: str):
    """
    Get information about a specific report
    
    Parameters:
    - filename: Name of the PDF file
    
    Returns:
    - Metadata about the report
    """
    # Security check
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    if not filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )
    
    file_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report '{filename}' not found"
        )
    
    try:
        from datetime import datetime
        
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        
        # Parse artist name from filename
        parts = filename.replace('.pdf', '').split('_Report_')
        artist_name = parts[0].replace('_', ' ') if parts else 'Unknown'
        
        return {
            "success": True,
            "filename": filename,
            "artist_name": artist_name,
            "download_url": f"/reports/download/{filename}",
            "path": file_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(modified_time).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting report info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting report info: {str(e)}"
        )

