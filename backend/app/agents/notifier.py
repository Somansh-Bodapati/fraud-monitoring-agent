"""
Notifier Agent - Sends alerts and notifications
"""
from typing import Dict, Any, Optional, List
from app.agents.base import BaseAgent
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Alert, Transaction, User, AlertSeverity
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotifierAgent(BaseAgent):
    """Agent responsible for sending alerts and notifications"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and send alerts
        
        Args:
            input_data: {
                "transaction": dict,
                "decision": dict,
                "alert_type": str (optional),
                "recipients": list (optional)
            }
        """
        transaction = input_data.get("transaction", {})
        decision = input_data.get("decision", {})
        alert_type = input_data.get("alert_type", "risk")
        
        self.log(f"Creating alert for transaction {transaction.get('id')}")
        
        db = SessionLocal()
        
        try:
            # Determine alert details
            severity = self._map_severity(decision.get("severity", "medium"))
            title = self._generate_alert_title(alert_type, transaction, decision)
            message = self._generate_alert_message(transaction, decision)
            recommendation = decision.get("recommendation", "")
            
            # Create alert in database
            alert = Alert(
                transaction_id=transaction.get("id"),
                user_id=transaction.get("user_id"),
                type=alert_type,
                severity=severity.value,
                title=title,
                message=message,
                recommendation=recommendation,
                extra_metadata={
                    "risk_score": decision.get("risk_score", 0.0),
                    "risk_factors": decision.get("risk_factors", []),
                    "actions": decision.get("actions", []),
                },
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Determine recipients
            recipients = input_data.get("recipients") or self._determine_recipients(
                db, transaction, severity
            )
            
            # Send notifications (in production, integrate with email/Slack)
            notification_result = await self._send_notifications(
                alert, recipients, transaction
            )
            
            self.log(f"Alert created: {alert.id}", data={"severity": severity.value})
            
            return {
                "status": "success",
                "alert_id": alert.id,
                "recipients": recipients,
                "notifications_sent": notification_result,
            }
        
        except Exception as e:
            self.log(f"Error creating alert: {str(e)}", level="ERROR")
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            db.close()
    
    def _map_severity(self, severity_str: str) -> AlertSeverity:
        """Map string severity to enum"""
        severity_map = {
            "low": AlertSeverity.LOW,
            "medium": AlertSeverity.MEDIUM,
            "high": AlertSeverity.HIGH,
            "critical": AlertSeverity.CRITICAL,
        }
        return severity_map.get(severity_str.lower(), AlertSeverity.MEDIUM)
    
    def _generate_alert_title(
        self, alert_type: str, transaction: Dict, decision: Dict
    ) -> str:
        """Generate alert title"""
        if alert_type == "anomaly":
            return f"Anomaly Detected: ${transaction.get('amount', 0):.2f} at {transaction.get('merchant', 'Unknown')}"
        elif alert_type == "fraud":
            return f"Potential Fraud Alert: ${transaction.get('amount', 0):.2f}"
        elif alert_type == "mismatch":
            return f"Receipt Mismatch: {transaction.get('merchant', 'Unknown')}"
        elif alert_type == "classification":
            return f"Classification Review Needed: {transaction.get('description', 'Transaction')}"
        else:
            return f"Transaction Alert: ${transaction.get('amount', 0):.2f}"
    
    def _generate_alert_message(self, transaction: Dict, decision: Dict) -> str:
        """Generate alert message"""
        risk_factors = decision.get("risk_factors", [])
        risk_score = decision.get("risk_score", 0.0)
        
        message = f"Transaction ${transaction.get('amount', 0):.2f} at {transaction.get('merchant', 'Unknown')} "
        message += f"has been flagged with a risk score of {risk_score:.2f}.\n\n"
        
        if risk_factors:
            message += "Risk factors:\n"
            for factor in risk_factors:
                message += f"• {factor}\n"
        
        return message
    
    def _determine_recipients(
        self, db: Session, transaction: Dict, severity: AlertSeverity
    ) -> List[int]:
        """Determine who should receive the alert"""
        recipients = []
        
        # Always notify the transaction owner
        if transaction.get("user_id"):
            recipients.append(transaction.get("user_id"))
        
        # For high/critical, notify managers and finance admins
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            managers = db.query(User).filter(
                User.role.in_(["manager", "finance_admin", "admin"]),
                User.is_active == True,
            ).all()
            recipients.extend([m.id for m in managers])
        
        return list(set(recipients))  # Remove duplicates
    
    async def _send_notifications(
        self, alert: Alert, recipients: List[int], transaction: Dict
    ) -> Dict[str, Any]:
        """Send notifications to recipients"""
        # In production, integrate with:
        # - Email service (SendGrid, SES)
        # - Slack/Teams webhooks
        # - In-app notifications
        
        # For MVP, just log
        self.log(
            f"Notifications sent to {len(recipients)} recipients",
            data={"alert_id": alert.id, "recipients": recipients}
        )
        
        return {
            "email": len(recipients),  # Mock: would send emails
            "in_app": len(recipients),  # Mock: would create in-app notifications
        }

