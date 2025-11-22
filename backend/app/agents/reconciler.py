"""
Reconciler Agent - Matches receipts to transactions
"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction, Receipt
import logging

logger = logging.getLogger(__name__)


class ReconcilerAgent(BaseAgent):
    """Agent responsible for reconciling receipts with transactions"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile receipt with transaction
        
        Args:
            input_data: {
                "receipt": dict (parsed receipt data),
                "transaction_id": int (optional),
                OR
                "transaction": dict,
                "receipt_id": int (optional)
            }
        """
        db = SessionLocal()
        
        try:
            receipt_data = input_data.get("receipt")
            transaction_data = input_data.get("transaction")
            transaction_id = input_data.get("transaction_id")
            receipt_id = input_data.get("receipt_id")
            
            # Get transaction and receipt from DB if IDs provided
            transaction = None
            receipt = None
            
            if transaction_id:
                transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            
            if receipt_id:
                receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
                if receipt:
                    receipt_data = {
                        "amount": receipt.amount,
                        "date": receipt.date.isoformat() if receipt.date else None,
                        "merchant": receipt.merchant,
                        "total": receipt.total,
                    }
            
            if not receipt_data and not transaction_data:
                return {
                    "status": "error",
                    "error": "No receipt or transaction data provided",
                }
            
            # If we have both, compare them
            if receipt_data and transaction_data:
                match_result = self._match_receipt_transaction(receipt_data, transaction_data)
                
                if match_result["is_match"]:
                    # Update transaction with receipt link
                    if transaction:
                        transaction.receipt_id = receipt.id if receipt else None
                        transaction.is_reconciled = True
                        db.commit()
                    
                    self.log("Receipt matched with transaction", data=match_result)
                else:
                    self.log("Receipt mismatch detected", data=match_result, level="WARNING")
                
                return {
                    "status": "success",
                    "is_reconciled": match_result["is_match"],
                    "match_result": match_result,
                }
            
            # If we only have receipt, try to find matching transaction
            elif receipt_data and not transaction_data:
                if transaction_id and transaction:
                    match_result = self._match_receipt_transaction(receipt_data, {
                        "amount": transaction.amount,
                        "date": transaction.date.isoformat() if transaction.date else None,
                        "merchant": transaction.merchant,
                    })
                    
                    if match_result["is_match"]:
                        transaction.receipt_id = receipt.id if receipt else None
                        transaction.is_reconciled = True
                        db.commit()
                    
                    return {
                        "status": "success",
                        "is_reconciled": match_result["is_match"],
                        "match_result": match_result,
                    }
                else:
                    # Try to find transaction by matching criteria
                    matching_transaction = self._find_matching_transaction(
                        db, receipt_data
                    )
                    
                    if matching_transaction:
                        matching_transaction.receipt_id = receipt.id if receipt else None
                        matching_transaction.is_reconciled = True
                        db.commit()
                        
                        return {
                            "status": "success",
                            "is_reconciled": True,
                            "transaction_id": matching_transaction.id,
                            "match_result": {"is_match": True, "confidence": 0.8},
                        }
                    else:
                        return {
                            "status": "success",
                            "is_reconciled": False,
                            "match_result": {
                                "is_match": False,
                                "reason": "No matching transaction found",
                            },
                        }
            
            return {
                "status": "error",
                "error": "Insufficient data for reconciliation",
            }
        
        except Exception as e:
            self.log(f"Error in reconciliation: {str(e)}", level="ERROR")
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            db.close()
    
    def _match_receipt_transaction(
        self, receipt: Dict[str, Any], transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match receipt data with transaction data"""
        receipt_amount = receipt.get("amount") or receipt.get("total", 0.0)
        transaction_amount = transaction.get("amount", 0.0)
        
        receipt_merchant = (receipt.get("merchant") or "").lower().strip()
        transaction_merchant = (transaction.get("merchant") or "").lower().strip()
        
        # Amount matching (allow 1% tolerance for rounding)
        amount_diff = abs(receipt_amount - transaction_amount)
        amount_match = amount_diff < max(transaction_amount * 0.01, 0.01)
        
        # Merchant matching (fuzzy)
        merchant_match = self._fuzzy_merchant_match(receipt_merchant, transaction_merchant)
        
        # Date matching (allow 7 days difference)
        date_match = True  # Simplified for MVP
        if receipt.get("date") and transaction.get("date"):
            try:
                from datetime import datetime
                receipt_date = datetime.fromisoformat(receipt["date"].replace("Z", "+00:00"))
                transaction_date = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
                date_diff = abs((receipt_date - transaction_date).days)
                date_match = date_diff <= 7
            except Exception:
                date_match = True
        
        # Calculate overall match
        is_match = amount_match and (merchant_match or date_match)
        confidence = 0.0
        if amount_match:
            confidence += 0.5
        if merchant_match:
            confidence += 0.3
        if date_match:
            confidence += 0.2
        
        return {
            "is_match": is_match,
            "confidence": confidence,
            "amount_match": amount_match,
            "merchant_match": merchant_match,
            "date_match": date_match,
            "amount_diff": amount_diff,
            "reason": self._generate_mismatch_reason(amount_match, merchant_match, date_match),
        }
    
    def _fuzzy_merchant_match(self, merchant1: str, merchant2: str) -> bool:
        """Fuzzy matching for merchant names"""
        if not merchant1 or not merchant2:
            return False
        
        # Simple substring matching
        if merchant1 in merchant2 or merchant2 in merchant1:
            return True
        
        # Word-based matching (if at least 2 words match)
        words1 = set(merchant1.split())
        words2 = set(merchant2.split())
        common_words = words1.intersection(words2)
        
        if len(common_words) >= 2:
            return True
        
        return False
    
    def _find_matching_transaction(
        self, db: Session, receipt_data: Dict[str, Any]
    ) -> Optional[Transaction]:
        """Find transaction that matches receipt"""
        receipt_amount = receipt_data.get("amount") or receipt_data.get("total", 0.0)
        receipt_merchant = (receipt_data.get("merchant") or "").lower()
        
        # Find transactions with similar amount (within 1%)
        tolerance = max(receipt_amount * 0.01, 0.01)
        transactions = db.query(Transaction).filter(
            Transaction.amount >= receipt_amount - tolerance,
            Transaction.amount <= receipt_amount + tolerance,
            Transaction.is_reconciled == False,
        ).all()
        
        # Filter by merchant if available
        if receipt_merchant:
            for txn in transactions:
                if self._fuzzy_merchant_match(receipt_merchant, (txn.merchant or "").lower()):
                    return txn
        
        # Return first match if no merchant match
        return transactions[0] if transactions else None
    
    def _generate_mismatch_reason(
        self, amount_match: bool, merchant_match: bool, date_match: bool
    ) -> str:
        """Generate reason for mismatch"""
        mismatches = []
        if not amount_match:
            mismatches.append("amount")
        if not merchant_match:
            mismatches.append("merchant")
        if not date_match:
            mismatches.append("date")
        
        if not mismatches:
            return "Perfect match"
        
        return f"Mismatch in: {', '.join(mismatches)}"

