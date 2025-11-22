"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    stripe_api_key: Optional[str] = None
    plaid_client_id: Optional[str] = None
    plaid_secret: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./fraud_monitoring.db"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Storage
    upload_dir: str = "./uploads"
    receipt_dir: str = "./uploads/receipts"
    
    # Agent Settings
    anomaly_threshold: float = 2.0  # Z-score threshold for anomaly detection
    confidence_threshold: float = 0.7  # Minimum confidence for auto-classification
    
    # LLM Settings
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

