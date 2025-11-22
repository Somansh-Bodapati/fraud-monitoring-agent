"""
Alert routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import Alert, UserRole

router = APIRouter()


class AlertResponse(BaseModel):
    id: int
    transaction_id: Optional[int]
    type: str
    severity: str
    title: str
    message: str
    recommendation: Optional[str]
    is_read: bool
    is_resolved: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_read: Optional[bool] = None,
    is_resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get alerts"""
    query = db.query(Alert)
    
    # Employees can only see their own alerts
    if current_user.role == UserRole.EMPLOYEE.value:
        query = query.filter(Alert.user_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Check permissions
    if current_user.role == UserRole.EMPLOYEE.value and alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    return alert


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Check permissions
    if current_user.role == UserRole.EMPLOYEE.value and alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    alert.is_read = True
    db.commit()
    
    return {"status": "success", "alert_id": alert_id}


@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user = Depends(require_role([UserRole.MANAGER, UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Resolve an alert (manager/admin only)"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    from datetime import datetime
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    db.commit()
    
    return {"status": "success", "alert_id": alert_id}

