"""
Database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    FINANCE_ADMIN = "finance_admin"
    ADMIN = "admin"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.EMPLOYEE.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    external_id = Column(String, unique=True, index=True)  # ID from external system
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String)
    merchant = Column(String)
    category = Column(String)  # Classified category
    subcategory = Column(String)
    status = Column(String, default=TransactionStatus.PENDING.value)
    
    # Anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    anomaly_reason = Column(Text)
    
    # Classification
    classification_confidence = Column(Float)
    classification_metadata = Column(JSON)
    
    # Reconciliation
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=True)
    is_reconciled = Column(Boolean, default=False)
    
    # Risk flags
    risk_score = Column(Float)
    risk_factors = Column(JSON)
    
    # Metadata
    source = Column(String)  # stripe, quickbooks, manual, etc.
    extra_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    receipt = relationship("Receipt", back_populates="transaction", uselist=False, foreign_keys="[Receipt.transaction_id]", primaryjoin="Transaction.id==Receipt.transaction_id")
    alerts = relationship("Alert", back_populates="transaction")


class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String)
    
    # Parsed data
    amount = Column(Float)
    date = Column(DateTime(timezone=True))
    merchant = Column(String)
    category = Column(String)
    line_items = Column(JSON)
    tax = Column(Float)
    total = Column(Float)
    
    # Parsing metadata
    parsing_confidence = Column(Float)
    parsing_metadata = Column(JSON)
    raw_text = Column(Text)
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="receipt", uselist=False, foreign_keys="[Receipt.transaction_id]", primaryjoin="Receipt.transaction_id==Transaction.id")


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Alert details
    type = Column(String, nullable=False)  # anomaly, fraud, mismatch, classification
    severity = Column(String, default=AlertSeverity.MEDIUM.value)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    extra_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Report details
    report_type = Column(String, nullable=False)  # weekly, monthly, custom
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Generated content
    summary = Column(Text)
    insights = Column(JSON)
    statistics = Column(JSON)
    
    # Generated by agent
    generated_by_agent = Column(Boolean, default=True)
    generation_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    
    # Feedback type
    feedback_type = Column(String, nullable=False)  # classification, anomaly, alert
    original_value = Column(JSON)  # What the agent predicted
    corrected_value = Column(JSON)  # What the user corrected it to
    comment = Column(Text)
    
    # Learning
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Integration details
    provider = Column(String, nullable=False)  # stripe, quickbooks, plaid, etc.
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Credentials (encrypted in production)
    credentials = Column(JSON)
    
    # Sync settings
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_frequency = Column(String, default="daily")  # realtime, hourly, daily
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

