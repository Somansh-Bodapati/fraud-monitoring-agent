"""
Report routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import Report, UserRole
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()


class ReportResponse(BaseModel):
    id: int
    report_type: str
    start_date: datetime
    end_date: datetime
    summary: Optional[str]
    insights: Optional[dict]
    statistics: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    report_type: str
    start_date: str
    end_date: str
    filters: Optional[dict] = None


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportCreate,
    current_user = Depends(require_role([UserRole.MANAGER, UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Generate a new report"""
    result = await orchestrator.generate_report(
        report_type=report_data.report_type,
        start_date=report_data.start_date,
        end_date=report_data.end_date,
        filters=report_data.filters or {},
    )
    
    if result.get("status") != "success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to generate report"),
        )
    
    # Get the created report
    report = db.query(Report).order_by(Report.created_at.desc()).first()
    
    return report


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    report_type: Optional[str] = None,
    current_user = Depends(require_role([UserRole.MANAGER, UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get all reports"""
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user = Depends(require_role([UserRole.MANAGER, UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get a specific report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    return report

