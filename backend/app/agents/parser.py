"""
Parser Agent - Processes receipts and invoices using LLM + OCR
"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.config import settings
from openai import OpenAI
from PIL import Image
import pytesseract
import logging
import json
import os

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    """Agent responsible for parsing receipts and invoices"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse receipt/invoice document
        
        Args:
            input_data: {
                "receipt": {
                    "file_path": str,
                    "file_type": str,
                    "user_id": int
                }
            }
        """
        receipt_data = input_data.get("receipt", {})
        file_path = receipt_data.get("file_path")
        file_type = receipt_data.get("file_type", "image")
        
        if not file_path or not os.path.exists(file_path):
            return {
                "status": "error",
                "error": "File not found",
            }
        
        self.log(f"Parsing receipt: {file_path}")
        
        try:
            # Step 1: Extract text using OCR (for images)
            if file_type in ["image", "jpg", "jpeg", "png", "pdf"]:
                raw_text = await self._extract_text_ocr(file_path)
            else:
                # For text files, read directly
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
            
            # Step 2: Use LLM to structure the data
            structured_data = await self._parse_with_llm(raw_text)
            
            # Step 3: Validate and clean
            parsed_data = self._validate_parsed_data(structured_data)
            
            self.log("Receipt parsed successfully", data={"merchant": parsed_data.get("merchant")})
            
            return {
                "status": "success",
                "parsed_data": parsed_data,
                "raw_text": raw_text,
                "confidence": parsed_data.get("confidence", 0.8),
            }
        
        except Exception as e:
            self.log(f"Error parsing receipt: {str(e)}", level="ERROR")
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def _extract_text_ocr(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}, trying LLM vision")
            # Fallback to LLM vision API
            return await self._extract_text_vision(file_path)
    
    async def _extract_text_vision(self, file_path: str) -> str:
        """Extract text using OpenAI Vision API"""
        try:
            with open(file_path, "rb") as image_file:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract all text from this receipt/invoice. Return only the raw text content."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_file.read()}"},
                                },
                            ],
                        }
                    ],
                    max_tokens=1000,
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Vision API extraction failed: {e}")
            return ""
    
    async def _parse_with_llm(self, raw_text: str) -> Dict[str, Any]:
        """Use LLM to parse and structure receipt data"""
        prompt = f"""Extract structured data from this receipt/invoice text. Return a JSON object with the following fields:
- amount: float (total amount)
- date: string (ISO format)
- merchant: string (vendor/merchant name)
- category: string (expense category: travel, meals, subscription, office_supplies, software, utilities, etc.)
- line_items: array of objects with "description" and "amount"
- tax: float (tax amount if present)
- total: float (total amount including tax)

Receipt text:
{raw_text}

Return ONLY valid JSON, no additional text."""

        response = self.client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": "You are a receipt parsing assistant. Extract structured data from receipts and return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.temperature,
            response_format={"type": "json_object"},
        )
        
        try:
            parsed = json.loads(response.choices[0].message.content)
            # Add confidence score based on completeness
            confidence = self._calculate_confidence(parsed)
            parsed["confidence"] = confidence
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"error": "Failed to parse response", "raw_text": raw_text}
    
    def _calculate_confidence(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness"""
        required_fields = ["amount", "date", "merchant"]
        optional_fields = ["category", "line_items", "tax"]
        
        score = 0.0
        for field in required_fields:
            if field in parsed_data and parsed_data[field]:
                score += 0.3
        
        for field in optional_fields:
            if field in parsed_data and parsed_data[field]:
                score += 0.1
        
        return min(score, 1.0)
    
    def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean parsed data"""
        # Ensure required fields exist
        validated = {
            "amount": data.get("amount", 0.0),
            "date": data.get("date", ""),
            "merchant": data.get("merchant", "Unknown"),
            "category": data.get("category", "uncategorized"),
            "line_items": data.get("line_items", []),
            "tax": data.get("tax", 0.0),
            "total": data.get("total", data.get("amount", 0.0)),
            "confidence": data.get("confidence", 0.5),
        }
        
        return validated

