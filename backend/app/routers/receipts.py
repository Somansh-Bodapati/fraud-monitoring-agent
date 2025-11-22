"""
Receipt routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.auth import get_current_user
from app.models import Receipt, Transaction
from app.agents.orchestrator import AgentOrchestrator
from app.config import settings
import os
import aiofiles
from datetime import datetime

router = APIRouter()
orchestrator = AgentOrchestrator()


class ReceiptResponse(BaseModel):
    id: int
    user_id: int
    transaction_id: Optional[int]
    file_name: str
    amount: Optional[float]
    date: Optional[datetime]
    merchant: Optional[str]
    category: Optional[str]
    is_processed: bool
    is_verified: bool
    parsing_confidence: Optional[float]

    class Config:
        from_attributes = True


@router.post("/upload", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    transaction_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and process a receipt"""
    # Create upload directory if it doesn't exist
    os.makedirs(settings.receipt_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.receipt_dir, f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Create receipt record
    receipt = Receipt(
        user_id=current_user.id,
        transaction_id=transaction_id,
        file_path=file_path,
        file_name=file.filename,
        file_type=file.content_type or "image",
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    # Process receipt through agent system
    try:
        receipt_data = {
            "file_path": file_path,
            "file_type": file.content_type or "image",
            "user_id": current_user.id,
            "transaction_id": transaction_id,
        }
        
        result = await orchestrator.process_receipt(receipt_data)
        
        # Update receipt with parsed data
        if result.get("status") == "success":
            parsed_data = result.get("parsing", {}).get("parsed_data", {})
            
            receipt.amount = parsed_data.get("amount")
            receipt.total = parsed_data.get("total", parsed_data.get("amount"))
            receipt.merchant = parsed_data.get("merchant")
            receipt.category = parsed_data.get("category")
            receipt.parsing_confidence = parsed_data.get("confidence", 0.0)
            receipt.parsing_metadata = parsed_data
            receipt.is_processed = True
            
            # Try to match with transaction
            if transaction_id:
                transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
                if transaction:
                    transaction.receipt_id = receipt.id
                    db.commit()
        
        db.commit()
        db.refresh(receipt)
    
    except Exception as e:
        print(f"Error processing receipt: {e}")
    
    return receipt


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a receipt"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )
    
    # Check permissions
    if receipt.user_id != current_user.id and current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    return receipt

