"""
Project scanner endpoints
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.scanner_service import ScannerService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ScanRequest(BaseModel):
    path: Optional[str] = None
    full_scan: bool = False

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

@router.post("/scan", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a project scan"""
    service = ScannerService(db)
    scan_id = service.start_scan(
        path=request.path,
        full_scan=request.full_scan,
        background_tasks=background_tasks
    )
    
    return ScanResponse(
        scan_id=scan_id,
        status="started",
        message="Scan started in background"
    )

@router.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str, db: Session = Depends(get_db)):
    """Get the status of a running scan"""
    service = ScannerService(db)
    status = service.get_scan_status(scan_id)
    
    if not status:
        return {"status": "not_found", "message": "Scan not found"}
    
    return status

@router.get("/last-scan")
async def get_last_scan_info(db: Session = Depends(get_db)):
    """Get information about the last completed scan"""
    service = ScannerService(db)
    return service.get_last_scan_info()

@router.post("/analyze-duplicates")
async def analyze_duplicates(db: Session = Depends(get_db)):
    """Analyze and identify duplicate projects"""
    service = ScannerService(db)
    result = service.analyze_duplicates()
    return result