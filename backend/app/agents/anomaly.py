"""
Anomaly Detection Agent - Detects fraud and outliers using statistical methods
"""
from typing import Dict, Any, Optional, List
from app.agents.base import BaseAgent
from app.config import settings
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AnomalyAgent(BaseAgent):
    """Agent responsible for detecting anomalies and potential fraud"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in a transaction
        
        Args:
            input_data: {
                "transaction": {
                    "id": int,
                    "amount": float,
                    "category": str,
                    "merchant": str,
                    "user_id": int,
                    "date": str
                },
                "classification": dict (optional)
            }
        """
        transaction = input_data.get("transaction", {})
        
        self.log(f"Analyzing transaction for anomalies: ${transaction.get('amount', 0)}")
        
        try:
            db = SessionLocal()
            user_id = transaction.get("user_id")
            amount = transaction.get("amount", 0.0)
            category = transaction.get("category", "other")
            merchant = transaction.get("merchant", "")
            
            # Get historical data for comparison
            historical = self._get_historical_data(db, user_id, category)
            
            # Run anomaly detection checks
            anomalies = []
            risk_score = 0.0
            
            # 1. Amount anomaly (Z-score)
            amount_anomaly = self._check_amount_anomaly(amount, historical, category)
            if amount_anomaly["is_anomaly"]:
                anomalies.append(amount_anomaly)
                risk_score += 0.4
            
            # 2. Merchant anomaly (new merchant)
            merchant_anomaly = self._check_merchant_anomaly(merchant, historical)
            if merchant_anomaly["is_anomaly"]:
                anomalies.append(merchant_anomaly)
                risk_score += 0.2
            
            # 3. Category pattern anomaly
            category_anomaly = self._check_category_anomaly(category, historical)
            if category_anomaly["is_anomaly"]:
                anomalies.append(category_anomaly)
                risk_score += 0.2
            
            # 4. Time-based anomaly (unusual time of day/month)
            time_anomaly = self._check_time_anomaly(transaction.get("date"), historical)
            if time_anomaly["is_anomaly"]:
                anomalies.append(time_anomaly)
                risk_score += 0.2
            
            # Normalize risk score
            risk_score = min(risk_score, 1.0)
            is_anomaly = len(anomalies) > 0 and risk_score >= 0.3
            
            result = {
                "status": "success",
                "is_anomaly": is_anomaly,
                "risk_score": risk_score,
                "anomalies": anomalies,
                "reason": self._generate_anomaly_reason(anomalies),
            }
            
            self.log(
                f"Anomaly detection complete: {'Anomaly detected' if is_anomaly else 'Normal'}",
                data={"risk_score": risk_score, "anomaly_count": len(anomalies)}
            )
            
            db.close()
            return result
        
        except Exception as e:
            self.log(f"Error in anomaly detection: {str(e)}", level="ERROR")
            return {
                "status": "error",
                "error": str(e),
                "is_anomaly": False,
                "risk_score": 0.0,
            }
    
    def _get_historical_data(
        self, db: Session, user_id: int, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get historical transactions for comparison"""
        query = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status != "rejected",
        )
        
        if category:
            query = query.filter(Transaction.category == category)
        
        # Get last 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        query = query.filter(Transaction.date >= cutoff_date)
        
        transactions = query.all()
        
        return [
            {
                "amount": t.amount,
                "merchant": t.merchant,
                "category": t.category,
                "date": t.date,
            }
            for t in transactions
        ]
    
    def _check_amount_anomaly(
        self, amount: float, historical: List[Dict], category: str
    ) -> Dict[str, Any]:
        """Check if amount is anomalous using Z-score"""
        if not historical:
            return {"is_anomaly": False, "type": "amount", "reason": "No historical data"}
        
        amounts = [h["amount"] for h in historical if h.get("amount")]
        if not amounts:
            return {"is_anomaly": False, "type": "amount", "reason": "No amount data"}
        
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        if std == 0:
            # All amounts are the same
            is_anomaly = abs(amount - mean) > mean * 0.5  # 50% difference
        else:
            z_score = abs((amount - mean) / std)
            is_anomaly = z_score > settings.anomaly_threshold
        
        return {
            "is_anomaly": is_anomaly,
            "type": "amount",
            "z_score": (amount - mean) / std if std > 0 else 0,
            "mean": mean,
            "std": std,
            "reason": f"Amount ${amount:.2f} is {'significantly higher' if amount > mean else 'significantly lower'} than average ${mean:.2f} for {category}",
        }
    
    def _check_merchant_anomaly(
        self, merchant: str, historical: List[Dict]
    ) -> Dict[str, Any]:
        """Check if merchant is new/unusual"""
        if not merchant:
            return {"is_anomaly": False, "type": "merchant"}
        
        merchants = [h.get("merchant", "").lower() for h in historical if h.get("merchant")]
        is_new = merchant.lower() not in merchants
        
        return {
            "is_anomaly": is_new and len(merchants) > 5,  # Only flag if we have enough history
            "type": "merchant",
            "is_new": is_new,
            "reason": f"New merchant: {merchant}" if is_new else "Known merchant",
        }
    
    def _check_category_anomaly(
        self, category: str, historical: List[Dict]
    ) -> Dict[str, Any]:
        """Check if category is unusual for this user"""
        if not historical:
            return {"is_anomaly": False, "type": "category"}
        
        categories = [h.get("category") for h in historical if h.get("category")]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        total = len(categories)
        if total == 0:
            return {"is_anomaly": False, "type": "category"}
        
        category_frequency = category_counts.get(category, 0) / total
        
        # Flag if category appears less than 5% of the time
        is_anomaly = category_frequency < 0.05 and total > 20
        
        return {
            "is_anomaly": is_anomaly,
            "type": "category",
            "frequency": category_frequency,
            "reason": f"Category '{category}' is unusual (appears in {category_frequency*100:.1f}% of transactions)",
        }
    
    def _check_time_anomaly(
        self, date_str: Optional[str], historical: List[Dict]
    ) -> Dict[str, Any]:
        """Check for time-based anomalies"""
        if not date_str:
            return {"is_anomaly": False, "type": "time"}
        
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            hour = date.hour
            
            # Flag transactions outside business hours (9 AM - 6 PM) as potentially unusual
            is_anomaly = hour < 9 or hour > 18
            
            return {
                "is_anomaly": is_anomaly,
                "type": "time",
                "hour": hour,
                "reason": f"Transaction at {hour}:00 (outside typical business hours)" if is_anomaly else "Normal business hours",
            }
        except Exception:
            return {"is_anomaly": False, "type": "time", "reason": "Could not parse date"}
    
    def _generate_anomaly_reason(self, anomalies: List[Dict]) -> str:
        """Generate human-readable reason for anomaly"""
        if not anomalies:
            return "No anomalies detected"
        
        reasons = [a.get("reason", "") for a in anomalies if a.get("is_anomaly")]
        return "; ".join(reasons) if reasons else "Multiple anomalies detected"

