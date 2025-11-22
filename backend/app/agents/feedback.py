"""
Feedback Agent - Processes user feedback to improve the system
"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Feedback, Transaction, Alert
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeedbackAgent(BaseAgent):
    """Agent responsible for processing user feedback and learning"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback
        
        Args:
            input_data: {
                "user_id": int,
                "feedback_type": "classification" | "anomaly" | "alert",
                "transaction_id": int (optional),
                "alert_id": int (optional),
                "original_value": dict,
                "corrected_value": dict,
                "comment": str (optional)
            }
        """
        user_id = input_data.get("user_id")
        feedback_type = input_data.get("feedback_type")
        transaction_id = input_data.get("transaction_id")
        alert_id = input_data.get("alert_id")
        original_value = input_data.get("original_value", {})
        corrected_value = input_data.get("corrected_value", {})
        comment = input_data.get("comment", "")
        
        self.log(f"Processing {feedback_type} feedback from user {user_id}")
        
        db = SessionLocal()
        
        try:
            # Create feedback record
            feedback = Feedback(
                user_id=user_id,
                transaction_id=transaction_id,
                alert_id=alert_id,
                feedback_type=feedback_type,
                original_value=original_value,
                corrected_value=corrected_value,
                comment=comment,
                is_processed=False,
            )
            
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            # Process feedback based on type
            if feedback_type == "classification":
                await self._process_classification_feedback(
                    db, feedback, transaction_id, original_value, corrected_value
                )
            elif feedback_type == "anomaly":
                await self._process_anomaly_feedback(
                    db, feedback, transaction_id, original_value, corrected_value
                )
            elif feedback_type == "alert":
                await self._process_alert_feedback(
                    db, feedback, alert_id, original_value, corrected_value
                )
            
            # Mark as processed
            feedback.is_processed = True
            feedback.processed_at = datetime.utcnow()
            db.commit()
            
            self.log(f"Feedback processed: {feedback.id}")
            
            return {
                "status": "success",
                "feedback_id": feedback.id,
                "message": "Feedback recorded and processed",
            }
        
        except Exception as e:
            self.log(f"Error processing feedback: {str(e)}", level="ERROR")
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            db.close()
    
    async def _process_classification_feedback(
        self,
        db: Session,
        feedback: Feedback,
        transaction_id: Optional[int],
        original: Dict,
        corrected: Dict,
    ):
        """Process classification feedback"""
        if not transaction_id:
            return
        
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return
        
        # Update transaction with corrected classification
        if "category" in corrected:
            transaction.category = corrected["category"]
        if "subcategory" in corrected:
            transaction.subcategory = corrected.get("subcategory")
        
        # Update classification metadata
        metadata = transaction.classification_metadata or {}
        metadata["corrected_by_user"] = True
        metadata["correction_date"] = datetime.utcnow().isoformat()
        transaction.classification_metadata = metadata
        
        db.commit()
        
        self.log(
            f"Classification corrected: {original.get('category')} -> {corrected.get('category')}",
            data={"transaction_id": transaction_id}
        )
    
    async def _process_anomaly_feedback(
        self,
        db: Session,
        feedback: Feedback,
        transaction_id: Optional[int],
        original: Dict,
        corrected: Dict,
    ):
        """Process anomaly feedback"""
        if not transaction_id:
            return
        
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return
        
        # If user says it's not an anomaly, update transaction
        if corrected.get("is_anomaly") == False and original.get("is_anomaly") == True:
            transaction.is_anomaly = False
            transaction.anomaly_score = 0.0
            transaction.anomaly_reason = "Marked as normal by user"
            
            # If transaction was flagged, consider approving it
            if transaction.status == "flagged":
                transaction.status = "pending"
            
            db.commit()
            
            self.log(
                f"Anomaly flag removed by user",
                data={"transaction_id": transaction_id}
            )
    
    async def _process_alert_feedback(
        self,
        db: Session,
        feedback: Feedback,
        alert_id: Optional[int],
        original: Dict,
        corrected: Dict,
    ):
        """Process alert feedback"""
        if not alert_id:
            return
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return
        
        # Mark alert as resolved if user confirms it's not an issue
        if corrected.get("is_valid") == False:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = feedback.user_id
            
            db.commit()
            
            self.log(
                f"Alert resolved by user",
                data={"alert_id": alert_id}
            )

