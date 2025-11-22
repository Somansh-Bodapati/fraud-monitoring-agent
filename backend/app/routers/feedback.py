"""
Feedback routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.auth import get_current_user
from app.models import Feedback
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()


class FeedbackCreate(BaseModel):
    feedback_type: str
    transaction_id: Optional[int] = None
    alert_id: Optional[int] = None
    original_value: dict
    corrected_value: dict
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    feedback_type: str
    transaction_id: Optional[int]
    alert_id: Optional[int]
    original_value: dict
    corrected_value: dict
    comment: Optional[str]
    is_processed: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit feedback"""
    result = await orchestrator.process_feedback({
        "user_id": current_user.id,
        "feedback_type": feedback_data.feedback_type,
        "transaction_id": feedback_data.transaction_id,
        "alert_id": feedback_data.alert_id,
        "original_value": feedback_data.original_value,
        "corrected_value": feedback_data.corrected_value,
        "comment": feedback_data.comment,
    })
    
    if result.get("status") != "success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to process feedback"),
        )
    
    # Get the created feedback
    feedback = db.query(Feedback).order_by(Feedback.created_at.desc()).first()
    
    return feedback


@router.get("/", response_model=list[FeedbackResponse])
async def get_feedback(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's feedback"""
    feedbacks = db.query(Feedback).filter(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedbacks

