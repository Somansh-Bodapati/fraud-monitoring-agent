"""
Classifier Agent - Intelligently classifies transactions into categories
"""
from typing import Dict, Any, Optional, List
from app.agents.base import BaseAgent
from app.config import settings
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)


class ClassifierAgent(BaseAgent):
    """Agent responsible for classifying transactions into expense categories"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.categories = [
            "travel",
            "meals",
            "subscription",
            "office_supplies",
            "software",
            "utilities",
            "marketing",
            "professional_services",
            "equipment",
            "rent",
            "insurance",
            "training",
            "entertainment",
            "transportation",
            "other",
        ]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a transaction
        
        Args:
            input_data: {
                "transaction": {
                    "amount": float,
                    "description": str,
                    "merchant": str,
                    "date": str,
                    "user_id": int,
                    "historical_patterns": list (optional)
                }
            }
        """
        transaction = input_data.get("transaction", {})
        
        self.log(f"Classifying transaction: {transaction.get('description', 'N/A')}")
        
        try:
            # Use LLM to classify
            classification = await self._classify_with_llm(transaction)
            
            # If confidence is low, mark for review
            confidence = classification.get("confidence", 0.0)
            if confidence < settings.confidence_threshold:
                classification["needs_review"] = True
                classification["review_reason"] = "Low confidence classification"
            
            self.log(
                f"Classified as: {classification.get('category')}",
                data={"confidence": confidence}
            )
            
            return {
                "status": "success",
                "classification": classification,
            }
        
        except Exception as e:
            self.log(f"Error classifying transaction: {str(e)}", level="ERROR")
            return {
                "status": "error",
                "error": str(e),
                "classification": {
                    "category": "uncategorized",
                    "confidence": 0.0,
                    "needs_review": True,
                },
            }
    
    async def _classify_with_llm(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to classify transaction"""
        description = transaction.get("description", "")
        merchant = transaction.get("merchant", "")
        amount = transaction.get("amount", 0.0)
        historical = transaction.get("historical_patterns", [])
        
        # Build context from historical patterns
        historical_context = ""
        if historical:
            recent_categories = [h.get("category") for h in historical[-5:]]
            historical_context = f"\n\nRecent transaction categories for this user: {', '.join(recent_categories)}"
        
        prompt = f"""Classify this business expense transaction into one of these categories:
{', '.join(self.categories)}

Transaction details:
- Description: {description}
- Merchant: {merchant}
- Amount: ${amount:.2f}
{historical_context}

Consider:
1. The merchant name and description
2. The amount (some categories have typical price ranges)
3. Historical patterns for this user
4. Common business expense patterns

Return a JSON object with:
- category: string (one of the categories above)
- subcategory: string (more specific, e.g., "airfare" for travel, "lunch" for meals)
- confidence: float (0.0 to 1.0)
- reasoning: string (brief explanation)

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at classifying business expenses. Be precise and consider context.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=settings.temperature,
            response_format={"type": "json_object"},
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            
            # Validate category
            if result.get("category") not in self.categories:
                result["category"] = "other"
                result["confidence"] = min(result.get("confidence", 0.5), 0.5)
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification response: {e}")
            return {
                "category": "other",
                "subcategory": "uncategorized",
                "confidence": 0.3,
                "reasoning": "Failed to parse classification",
            }

