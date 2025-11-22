package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Alert;
import com.fraudmonitoring.entity.AlertSeverity;
import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotifierAgentService {
    
    private final AlertRepository alertRepository;
    
    public void sendAlert(Transaction transaction) {
        try {
            AlertSeverity severity = transaction.getRiskScore() >= 0.7 
                    ? AlertSeverity.HIGH 
                    : AlertSeverity.MEDIUM;
            
            Alert alert = Alert.builder()
                    .transaction(transaction)
                    .user(transaction.getUser())
                    .type("anomaly")
                    .severity(severity)
                    .title(String.format("Anomaly Detected: $%.2f at %s", 
                            transaction.getAmount(), 
                            transaction.getMerchant() != null ? transaction.getMerchant() : "Unknown"))
                    .message(transaction.getAnomalyReason() != null 
                            ? transaction.getAnomalyReason() 
                            : "Transaction flagged as anomalous")
                    .recommendation("Please review this transaction for potential fraud or errors")
                    .build();
            
            alertRepository.save(alert);
            log.info("Alert created for transaction: {}", transaction.getId());
        } catch (Exception e) {
            log.error("Error sending alert: {}", transaction.getId(), e);
        }
    }
}

