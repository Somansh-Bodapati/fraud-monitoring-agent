"""
Transaction routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models import Transaction, User, TransactionStatus, UserRole
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()


class TransactionCreate(BaseModel):
    amount: float
    currency: str = "USD"
    date: str
    description: Optional[str] = None
    merchant: Optional[str] = None
    source: str = "manual"
    receipt_id: Optional[int] = None
    metadata: Optional[dict] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    currency: str
    date: datetime
    description: Optional[str]
    merchant: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    status: str
    is_anomaly: bool
    anomaly_score: Optional[float]
    risk_score: Optional[float]
    is_reconciled: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction and process it through the agent system"""
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        date=datetime.fromisoformat(transaction_data.date.replace("Z", "+00:00")),
        description=transaction_data.description,
        merchant=transaction_data.merchant,
        source=transaction_data.source,
        receipt_id=transaction_data.receipt_id,
        extra_metadata=transaction_data.metadata or {},
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Process through agent system
    try:
        transaction_dict = {
            "id": transaction.id,
            "amount": transaction.amount,
            "description": transaction.description,
            "merchant": transaction.merchant,
            "date": transaction.date.isoformat(),
            "user_id": transaction.user_id,
            "category": transaction.category,
            "receipt_id": transaction.receipt_id,
        }
        
        result = await orchestrator.process_transaction(transaction_dict)
        
        # Update transaction with agent results
        if result.get("status") == "success":
            classification = result.get("classification", {}).get("classification", {})
            anomaly = result.get("anomaly", {})
            decision = result.get("decision", {})
            
            if classification:
                transaction.category = classification.get("category")
                transaction.subcategory = classification.get("subcategory")
                transaction.classification_confidence = classification.get("confidence")
                transaction.classification_metadata = classification
            
            if anomaly:
                transaction.is_anomaly = anomaly.get("is_anomaly", False)
                transaction.anomaly_score = anomaly.get("risk_score")
                transaction.anomaly_reason = anomaly.get("reason")
            
            if decision:
                transaction.risk_score = decision.get("risk_score")
                transaction.risk_factors = decision.get("risk_factors", [])
                if decision.get("severity") in ["high", "critical"]:
                    transaction.status = TransactionStatus.FLAGGED.value
        
        db.commit()
        db.refresh(transaction)
    
    except Exception as e:
        # Log error but don't fail the transaction creation
        print(f"Error processing transaction through agents: {e}")
    
    return transaction


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    is_anomaly: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transactions (filtered by user role)"""
    query = db.query(Transaction)
    
    # Employees can only see their own transactions
    if current_user.role == UserRole.EMPLOYEE.value:
        query = query.filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Transaction.status == status_filter)
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
    if is_anomaly is not None:
        query = query.filter(Transaction.is_anomaly == is_anomaly)
    
    transactions = query.order_by(desc(Transaction.date)).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific transaction"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Check permissions
    if current_user.role == UserRole.EMPLOYEE.value and transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this transaction",
        )
    
    return transaction


@router.patch("/{transaction_id}/status")
async def update_transaction_status(
    transaction_id: int,
    new_status: str = Query(..., alias="new_status"),
    current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.FINANCE_ADMIN, UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Update transaction status (manager/admin only)"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    if new_status not in [s.value for s in TransactionStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )
    
    transaction.status = new_status
    db.commit()
    db.refresh(transaction)
    
    return {"status": "success", "transaction_id": transaction_id, "new_status": new_status}

