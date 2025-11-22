"""
Integration routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import Integration, UserRole

router = APIRouter()


class IntegrationCreate(BaseModel):
    provider: str
    name: str
    credentials: dict
    sync_frequency: str = "daily"


class IntegrationResponse(BaseModel):
    id: int
    provider: str
    name: str
    is_active: bool
    sync_frequency: str
    last_sync_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    current_user = Depends(require_role([UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Create a new integration"""
    integration = Integration(
        user_id=current_user.id,
        provider=integration_data.provider,
        name=integration_data.name,
        credentials=integration_data.credentials,
        sync_frequency=integration_data.sync_frequency,
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return integration


@router.get("/", response_model=List[IntegrationResponse])
async def get_integrations(
    current_user = Depends(require_role([UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Get all integrations"""
    integrations = db.query(Integration).filter(Integration.is_active == True).all()
    return integrations

