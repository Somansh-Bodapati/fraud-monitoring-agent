"""
Agent orchestrator for coordinating multi-agent workflows
"""
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent
from app.agents.data_retriever import DataRetrieverAgent
from app.agents.parser import ParserAgent
from app.agents.classifier import ClassifierAgent
from app.agents.anomaly import AnomalyAgent
from app.agents.reconciler import ReconcilerAgent
from app.agents.decision import DecisionAgent
from app.agents.notifier import NotifierAgent
from app.agents.reporter import ReporterAgent
from app.agents.feedback import FeedbackAgent
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent workflows"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents"""
        self.agents = {
            "data_retriever": DataRetrieverAgent("DataRetriever", self.config),
            "parser": ParserAgent("Parser", self.config),
            "classifier": ClassifierAgent("Classifier", self.config),
            "anomaly": AnomalyAgent("Anomaly", self.config),
            "reconciler": ReconcilerAgent("Reconciler", self.config),
            "decision": DecisionAgent("Decision", self.config),
            "notifier": NotifierAgent("Notifier", self.config),
            "reporter": ReporterAgent("Reporter", self.config),
            "feedback": FeedbackAgent("Feedback", self.config),
        }
    
    async def process_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full workflow for processing a new transaction
        
        Flow:
        1. Retrieve transaction data (if needed)
        2. Parse any associated receipts
        3. Classify transaction
        4. Detect anomalies
        5. Reconcile with receipts
        6. Make decisions about risk
        7. Send notifications if needed
        """
        workflow_log = []
        results = {}
        
        try:
            # Step 1: Classify transaction
            logger.info("Classifying transaction...")
            classification_result = await self.agents["classifier"].execute({
                "transaction": transaction_data,
            })
            results["classification"] = classification_result
            workflow_log.append({"step": "classification", "result": classification_result})
            
            # Step 2: Detect anomalies
            logger.info("Detecting anomalies...")
            anomaly_result = await self.agents["anomaly"].execute({
                "transaction": transaction_data,
                "classification": classification_result,
            })
            results["anomaly"] = anomaly_result
            workflow_log.append({"step": "anomaly_detection", "result": anomaly_result})
            
            # Step 3: Reconcile with receipts (if receipt_id provided)
            if transaction_data.get("receipt_id"):
                logger.info("Reconciling with receipt...")
                reconciliation_result = await self.agents["reconciler"].execute({
                    "transaction": transaction_data,
                    "receipt_id": transaction_data["receipt_id"],
                })
                results["reconciliation"] = reconciliation_result
                workflow_log.append({"step": "reconciliation", "result": reconciliation_result})
            
            # Step 4: Make decision about risk and actions
            logger.info("Making risk decision...")
            decision_result = await self.agents["decision"].execute({
                "transaction": transaction_data,
                "classification": classification_result,
                "anomaly": anomaly_result,
                "reconciliation": results.get("reconciliation"),
            })
            results["decision"] = decision_result
            workflow_log.append({"step": "decision", "result": decision_result})
            
            # Step 5: Send notifications if needed
            if decision_result.get("should_alert"):
                logger.info("Sending notifications...")
                notification_result = await self.agents["notifier"].execute({
                    "transaction": transaction_data,
                    "decision": decision_result,
                })
                results["notification"] = notification_result
                workflow_log.append({"step": "notification", "result": notification_result})
            
            results["workflow_log"] = workflow_log
            results["status"] = "success"
            
        except Exception as e:
            logger.error(f"Error in transaction processing workflow: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
            results["workflow_log"] = workflow_log
        
        return results
    
    async def process_receipt(self, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a receipt document
        
        Flow:
        1. Parse receipt
        2. Attempt to match with existing transaction
        3. If matched, reconcile
        4. If not matched, create alert
        """
        workflow_log = []
        results = {}
        
        try:
            # Step 1: Parse receipt
            logger.info("Parsing receipt...")
            parse_result = await self.agents["parser"].execute({
                "receipt": receipt_data,
            })
            results["parsing"] = parse_result
            workflow_log.append({"step": "parsing", "result": parse_result})
            
            # Step 2: Try to reconcile with transaction
            if receipt_data.get("transaction_id"):
                logger.info("Reconciling receipt with transaction...")
                reconciliation_result = await self.agents["reconciler"].execute({
                    "receipt": parse_result,
                    "transaction_id": receipt_data["transaction_id"],
                })
                results["reconciliation"] = reconciliation_result
                workflow_log.append({"step": "reconciliation", "result": reconciliation_result})
            
            results["workflow_log"] = workflow_log
            results["status"] = "success"
            
        except Exception as e:
            logger.error(f"Error in receipt processing workflow: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
            results["workflow_log"] = workflow_log
        
        return results
    
    async def generate_report(
        self, 
        report_type: str, 
        start_date: str, 
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate automated report"""
        return await self.agents["reporter"].execute({
            "report_type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "filters": filters or {},
        })
    
    async def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user feedback to improve system"""
        return await self.agents["feedback"].execute(feedback_data)
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a specific agent by name"""
        return self.agents.get(agent_name)

