"""
Reporter Agent - Generates automated reports
"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.config import settings
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction, Alert, Report
from datetime import datetime, timedelta
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)


class ReporterAgent(BaseAgent):
    """Agent responsible for generating automated reports"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate automated report
        
        Args:
            input_data: {
                "report_type": "weekly" | "monthly" | "custom",
                "start_date": str (ISO format),
                "end_date": str (ISO format),
                "filters": dict (optional),
                "user_id": int (optional)
            }
        """
        report_type = input_data.get("report_type", "monthly")
        start_date_str = input_data.get("start_date")
        end_date_str = input_data.get("end_date")
        filters = input_data.get("filters", {})
        user_id = input_data.get("user_id")
        
        self.log(f"Generating {report_type} report")
        
        db = SessionLocal()
        
        try:
            # Parse dates
            start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            
            # Gather data
            statistics = self._gather_statistics(db, start_date, end_date, user_id, filters)
            insights = self._generate_insights(statistics)
            
            # Generate natural language summary using LLM
            summary = await self._generate_summary(statistics, insights, report_type)
            
            # Create report record
            report = Report(
                user_id=user_id or 1,  # Default to admin
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                summary=summary,
                insights=insights,
                statistics=statistics,
                generated_by_agent=True,
                generation_metadata={
                    "model": settings.model_name,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            self.log(f"Report generated: {report.id}")
            
            return {
                "status": "success",
                "report_id": report.id,
                "summary": summary,
                "insights": insights,
                "statistics": statistics,
            }
        
        except Exception as e:
            self.log(f"Error generating report: {str(e)}", level="ERROR")
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            db.close()
    
    def _gather_statistics(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int],
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Gather statistics for the report period"""
        query = db.query(Transaction).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        if filters.get("status"):
            query = query.filter(Transaction.status == filters["status"])
        
        transactions = query.all()
        
        # Calculate statistics
        total_amount = sum(t.amount for t in transactions)
        total_count = len(transactions)
        avg_amount = total_amount / total_count if total_count > 0 else 0
        
        # By category
        category_breakdown = {}
        for t in transactions:
            cat = t.category or "uncategorized"
            if cat not in category_breakdown:
                category_breakdown[cat] = {"count": 0, "amount": 0.0}
            category_breakdown[cat]["count"] += 1
            category_breakdown[cat]["amount"] += t.amount
        
        # Anomalies
        anomaly_count = sum(1 for t in transactions if t.is_anomaly)
        flagged_count = sum(1 for t in transactions if t.status == "flagged")
        
        # Alerts
        alerts_query = db.query(Alert).filter(
            Alert.created_at >= start_date,
            Alert.created_at <= end_date,
        )
        if user_id:
            alerts_query = alerts_query.filter(Alert.user_id == user_id)
        alerts = alerts_query.all()
        
        alert_count = len(alerts)
        high_risk_alerts = sum(1 for a in alerts if a.severity == "high" or a.severity == "critical")
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "transactions": {
                "total_count": total_count,
                "total_amount": total_amount,
                "average_amount": avg_amount,
                "anomaly_count": anomaly_count,
                "flagged_count": flagged_count,
            },
            "category_breakdown": category_breakdown,
            "alerts": {
                "total": alert_count,
                "high_risk": high_risk_alerts,
            },
        }
    
    def _generate_insights(self, statistics: Dict[str, Any]) -> list:
        """Generate insights from statistics"""
        insights = []
        
        transactions = statistics.get("transactions", {})
        category_breakdown = statistics.get("category_breakdown", {})
        
        # Top spending category
        if category_breakdown:
            top_category = max(
                category_breakdown.items(),
                key=lambda x: x[1]["amount"]
            )
            insights.append({
                "type": "top_category",
                "category": top_category[0],
                "amount": top_category[1]["amount"],
                "message": f"Highest spending category: {top_category[0]} (${top_category[1]['amount']:.2f})",
            })
        
        # Anomaly rate
        total_count = transactions.get("total_count", 0)
        anomaly_count = transactions.get("anomaly_count", 0)
        if total_count > 0:
            anomaly_rate = (anomaly_count / total_count) * 100
            if anomaly_rate > 10:
                insights.append({
                    "type": "high_anomaly_rate",
                    "rate": anomaly_rate,
                    "message": f"High anomaly rate: {anomaly_rate:.1f}% of transactions flagged",
                })
        
        # Alert trend
        alert_count = statistics.get("alerts", {}).get("total", 0)
        if alert_count > 0:
            insights.append({
                "type": "alerts",
                "count": alert_count,
                "message": f"{alert_count} alerts generated during this period",
            })
        
        return insights
    
    async def _generate_summary(
        self, statistics: Dict[str, Any], insights: list, report_type: str
    ) -> str:
        """Generate natural language summary using LLM"""
        prompt = f"""Generate a concise executive summary for a {report_type} expense monitoring report.

Statistics:
- Total Transactions: {statistics.get('transactions', {}).get('total_count', 0)}
- Total Amount: ${statistics.get('transactions', {}).get('total_amount', 0):.2f}
- Average Transaction: ${statistics.get('transactions', {}).get('average_amount', 0):.2f}
- Anomalies Detected: {statistics.get('transactions', {}).get('anomaly_count', 0)}
- Alerts Generated: {statistics.get('alerts', {}).get('total', 0)}

Key Insights:
{chr(10).join(f"- {i.get('message', '')}" for i in insights)}

Category Breakdown:
{json.dumps(statistics.get('category_breakdown', {}), indent=2)}

Write a 2-3 paragraph executive summary that:
1. Highlights key metrics and trends
2. Identifies areas of concern (anomalies, high-risk transactions)
3. Provides actionable recommendations

Be professional and concise."""

        response = self.client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst writing executive summaries for expense reports.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        
        return response.choices[0].message.content

