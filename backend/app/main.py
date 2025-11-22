"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import (
    auth,
    transactions,
    receipts,
    alerts,
    reports,
    feedback,
    integrations,
    dashboard,
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense & Fraud Monitoring Agent API",
    description="Autonomous AI agent system for expense monitoring and fraud detection",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    return {
        "message": "Expense & Fraud Monitoring Agent API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

