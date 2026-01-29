"""
Data Management API Router
Provides endpoints for uploading and managing CSV data files
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import shutil
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data-management"])

# Define the processed data directory
PROCESSED_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "data", 
    "processed"
)

# Ensure the directory exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(..., description="CSV file to upload")
):
    """
    Upload a CSV file to data/processed directory
    
    Parameters:
    - file: CSV file to upload
    
    Returns:
    - filename: Name of the uploaded file
    - path: Full path where file was saved
    - rows: Number of rows in the CSV
    - columns: List of column names
    - size_bytes: File size in bytes
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Only CSV files are allowed"
        )
    
    try:
        # Create a safe filename with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(file.filename)[0]
        safe_filename = f"{base_name}_{timestamp}.csv"
        file_path = os.path.join(PROCESSED_DATA_DIR, safe_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"✅ File uploaded successfully: {file_path}")
        
        # Read the CSV to get metadata
        try:
            df = pd.read_csv(file_path)
            rows = len(df)
            columns = df.columns.tolist()
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "File uploaded successfully",
                    "filename": safe_filename,
                    "original_filename": file.filename,
                    "path": file_path,
                    "rows": rows,
                    "columns": columns,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                }
            )
        except Exception as e:
            # If we can't read the CSV, still return success but with limited info
            logger.warning(f"⚠️ Could not read CSV metadata: {str(e)}")
            file_size = os.path.getsize(file_path)
            
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "File uploaded successfully (metadata unavailable)",
                    "filename": safe_filename,
                    "original_filename": file.filename,
                    "path": file_path,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "warning": "Could not read CSV metadata"
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/upload-csv-batch")
async def upload_csv_batch(
    files: List[UploadFile] = File(..., description="Multiple CSV files to upload")
):
    """
    Upload multiple CSV files at once
    
    Parameters:
    - files: List of CSV files to upload
    
    Returns:
    - uploaded: List of successfully uploaded files with metadata
    - failed: List of files that failed to upload
    - total: Total number of files processed
    """
    uploaded = []
    failed = []
    
    for file in files:
        # Validate file extension
        if not file.filename.endswith('.csv'):
            failed.append({
                "filename": file.filename,
                "error": "Only CSV files are allowed"
            })
            continue
        
        try:
            # Create a safe filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(file.filename)[0]
            safe_filename = f"{base_name}_{timestamp}.csv"
            file_path = os.path.join(PROCESSED_DATA_DIR, safe_filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get metadata
            try:
                df = pd.read_csv(file_path)
                rows = len(df)
                columns = df.columns.tolist()
                file_size = os.path.getsize(file_path)
                
                uploaded.append({
                    "filename": safe_filename,
                    "original_filename": file.filename,
                    "path": file_path,
                    "rows": rows,
                    "columns": columns,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                })
            except Exception as e:
                # Still count as uploaded even if metadata fails
                file_size = os.path.getsize(file_path)
                uploaded.append({
                    "filename": safe_filename,
                    "original_filename": file.filename,
                    "path": file_path,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "warning": f"Could not read metadata: {str(e)}"
                })
            
            logger.info(f"✅ File uploaded: {safe_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error uploading {file.filename}: {str(e)}")
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(failed) == 0,
        "total": len(files),
        "uploaded_count": len(uploaded),
        "failed_count": len(failed),
        "uploaded": uploaded,
        "failed": failed
    }


@router.get("/list-files")
async def list_files():
    """
    List all CSV files in the data/processed directory
    
    Returns:
    - files: List of files with metadata
    - total_count: Total number of files
    - total_size_mb: Total size of all files
    """
    try:
        files = []
        total_size = 0
        
        for filename in os.listdir(PROCESSED_DATA_DIR):
            if filename.endswith('.csv'):
                file_path = os.path.join(PROCESSED_DATA_DIR, filename)
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                total_size += file_size
                
                # Try to get row count
                try:
                    df = pd.read_csv(file_path)
                    rows = len(df)
                    columns = len(df.columns)
                except:
                    rows = None
                    columns = None
                
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "modified_at": datetime.fromtimestamp(modified_time).isoformat(),
                    "rows": rows,
                    "columns": columns
                })
        
        # Sort by modified time (newest first)
        files.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return {
            "success": True,
            "files": files,
            "total_count": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )


@router.delete("/delete-file/{filename}")
async def delete_file(filename: str):
    """
    Delete a CSV file from data/processed directory
    
    Parameters:
    - filename: Name of the file to delete
    
    Returns:
    - success: Whether the deletion was successful
    - message: Status message
    """
    # Security check: ensure filename doesn't contain path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    file_path = os.path.join(PROCESSED_DATA_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found"
        )
    
    try:
        os.remove(file_path)
        logger.info(f"🗑️ File deleted: {filename}")
        
        return {
            "success": True,
            "message": f"File '{filename}' deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get("/file-info/{filename}")
async def get_file_info(filename: str):
    """
    Get detailed information about a specific CSV file
    
    Parameters:
    - filename: Name of the file
    
    Returns:
    - Detailed metadata including preview of first few rows
    """
    # Security check
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    file_path = os.path.join(PROCESSED_DATA_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found"
        )
    
    try:
        # Get file stats
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Get data types
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Get sample data (first 5 rows)
        preview = df.head(5).to_dict(orient='records')
        
        # Get basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        statistics = {}
        for col in numeric_cols:
            statistics[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median())
            }
        
        return {
            "success": True,
            "filename": filename,
            "path": file_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "modified_at": datetime.fromtimestamp(modified_time).isoformat(),
            "rows": len(df),
            "columns": df.columns.tolist(),
            "column_count": len(df.columns),
            "data_types": dtypes,
            "preview": preview,
            "statistics": statistics if statistics else None
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting file info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )

