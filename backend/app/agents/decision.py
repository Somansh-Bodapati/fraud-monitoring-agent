"""
Decision Agent - Reasons about risk and recommends actions
"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.config import settings
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)


class DecisionAgent(BaseAgent):
    """Agent responsible for making decisions about risk and recommending actions"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decision about transaction risk and actions
        
        Args:
            input_data: {
                "transaction": dict,
                "classification": dict,
                "anomaly": dict,
                "reconciliation": dict (optional)
            }
        """
        transaction = input_data.get("transaction", {})
        classification = input_data.get("classification", {}).get("classification", {})
        anomaly = input_data.get("anomaly", {})
        reconciliation = input_data.get("reconciliation", {})
        
        self.log("Making risk decision for transaction")
        
        try:
            # Aggregate risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Classification risk
            if classification.get("needs_review"):
                risk_factors.append("Low classification confidence")
                risk_score += 0.2
            
            # Anomaly risk
            if anomaly.get("is_anomaly"):
                risk_factors.append(f"Anomaly detected: {anomaly.get('reason', '')}")
                risk_score += anomaly.get("risk_score", 0.0) * 0.6
            
            # Reconciliation risk
            if reconciliation:
                if not reconciliation.get("is_reconciled"):
                    risk_factors.append("Receipt mismatch or missing")
                    risk_score += 0.3
            
            # Use LLM to reason about overall risk and recommend actions
            decision = await self._reason_about_risk(
                transaction, classification, anomaly, risk_factors, risk_score
            )
            
            # Determine if alert is needed
            should_alert = risk_score >= 0.4 or decision.get("severity") in ["high", "critical"]
            
            result = {
                "status": "success",
                "risk_score": min(risk_score, 1.0),
                "risk_factors": risk_factors,
                "severity": decision.get("severity", "low"),
                "recommendation": decision.get("recommendation", ""),
                "actions": decision.get("actions", []),
                "should_alert": should_alert,
            }
            
            self.log(
                f"Decision made: {result['severity']} risk",
                data={"risk_score": result["risk_score"], "should_alert": should_alert}
            )
            
            return result
        
        except Exception as e:
            self.log(f"Error in decision making: {str(e)}", level="ERROR")
            return {
                "status": "error",
                "error": str(e),
                "risk_score": 0.5,
                "severity": "medium",
                "should_alert": True,
                "recommendation": "Manual review required due to processing error",
            }
    
    async def _reason_about_risk(
        self,
        transaction: Dict[str, Any],
        classification: Dict[str, Any],
        anomaly: Dict[str, Any],
        risk_factors: list,
        risk_score: float,
    ) -> Dict[str, Any]:
        """Use LLM to reason about risk and recommend actions"""
        prompt = f"""Analyze this business expense transaction and provide risk assessment and recommendations.

Transaction:
- Amount: ${transaction.get('amount', 0):.2f}
- Merchant: {transaction.get('merchant', 'Unknown')}
- Description: {transaction.get('description', 'N/A')}
- Category: {classification.get('category', 'uncategorized')}

Risk Factors:
{chr(10).join(f"- {factor}" for factor in risk_factors) if risk_factors else "- None identified"}

Anomaly Details:
{anomaly.get('reason', 'No anomalies detected')}

Risk Score: {risk_score:.2f}/1.0

Provide:
1. Severity level: low, medium, high, or critical
2. A clear recommendation for what action to take
3. Specific actions: list of actions like ["flag_for_review", "request_receipt", "manager_approval", "auto_approve"]

Return JSON with:
- severity: string
- recommendation: string (human-readable)
- actions: array of strings

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial risk analyst. Assess transaction risk and recommend appropriate actions.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,  # Lower temperature for more consistent decisions
            response_format={"type": "json_object"},
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse decision response: {e}")
            # Fallback decision
            if risk_score >= 0.7:
                severity = "high"
                recommendation = "High risk transaction - requires immediate review"
                actions = ["flag_for_review", "manager_approval"]
            elif risk_score >= 0.4:
                severity = "medium"
                recommendation = "Medium risk - review recommended"
                actions = ["flag_for_review"]
            else:
                severity = "low"
                recommendation = "Low risk - appears normal"
                actions = ["auto_approve"]
            
            return {
                "severity": severity,
                "recommendation": recommendation,
                "actions": actions,
            }

