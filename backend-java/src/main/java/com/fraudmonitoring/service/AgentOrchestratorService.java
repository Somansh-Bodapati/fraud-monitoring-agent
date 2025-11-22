package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class AgentOrchestratorService {
    
    private final ClassifierAgentService classifierAgentService;
    private final AnomalyAgentService anomalyAgentService;
    private final DecisionAgentService decisionAgentService;
    private final NotifierAgentService notifierAgentService;
    
    @Async
    public void processTransaction(Transaction transaction) {
        try {
            log.info("Processing transaction: {}", transaction.getId());
            
            // Classify transaction
            classifierAgentService.classifyTransaction(transaction);
            
            // Detect anomalies
            anomalyAgentService.detectAnomalies(transaction);
            
            // Make decision
            decisionAgentService.makeDecision(transaction);
            
            // Send notifications if needed
            if (transaction.getRiskScore() != null && transaction.getRiskScore() >= 0.4) {
                notifierAgentService.sendAlert(transaction);
            }
            
        } catch (Exception e) {
            log.error("Error processing transaction: {}", transaction.getId(), e);
        }
    }
}

