"""
Dashboard routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import Transaction, Alert, UserRole

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics"""
    # Base query
    query = db.query(Transaction)
    
    # Employees can only see their own stats
    if current_user.role == UserRole.EMPLOYEE.value:
        query = query.filter(Transaction.user_id == current_user.id)
    
    # Last 30 days
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    recent_query = query.filter(Transaction.date >= cutoff_date)
    
    # Total transactions
    total_count = recent_query.count()
    
    # Total amount
    total_amount = recent_query.with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    
    # Anomalies
    anomaly_count = recent_query.filter(Transaction.is_anomaly == True).count()
    
    # Flagged
    flagged_count = recent_query.filter(Transaction.status == "flagged").count()
    
    # Alerts
    alert_query = db.query(Alert).filter(Alert.created_at >= cutoff_date)
    if current_user.role == UserRole.EMPLOYEE.value:
        alert_query = alert_query.filter(Alert.user_id == current_user.id)
    
    alert_count = alert_query.count()
    unread_alerts = alert_query.filter(Alert.is_read == False).count()
    
    # Category breakdown
    category_stats = (
        recent_query.with_entities(
            Transaction.category,
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.amount).label("total"),
        )
        .group_by(Transaction.category)
        .all()
    )
    
    category_breakdown = [
        {"category": cat or "uncategorized", "count": count, "total": float(total or 0)}
        for cat, count, total in category_stats
    ]
    
    return {
        "transactions": {
            "total": total_count,
            "total_amount": float(total_amount),
            "anomalies": anomaly_count,
            "flagged": flagged_count,
        },
        "alerts": {
            "total": alert_count,
            "unread": unread_alerts,
        },
        "category_breakdown": category_breakdown,
    }

