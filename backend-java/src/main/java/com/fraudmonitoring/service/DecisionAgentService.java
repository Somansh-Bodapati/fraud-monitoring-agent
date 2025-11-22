package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.entity.TransactionStatus;
import com.fraudmonitoring.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DecisionAgentService {
    
    private final TransactionRepository transactionRepository;
    
    public void makeDecision(Transaction transaction) {
        try {
            List<String> riskFactors = new ArrayList<>();
            double riskScore = 0.0;
            
            if (transaction.getIsAnomaly() != null && transaction.getIsAnomaly()) {
                riskFactors.add("Anomaly detected");
                riskScore += 0.6;
            }
            
            if (transaction.getClassificationConfidence() != null && 
                transaction.getClassificationConfidence() < 0.7) {
                riskFactors.add("Low classification confidence");
                riskScore += 0.2;
            }
            
            transaction.setRiskScore(riskScore);
            transaction.setRiskFactors(riskFactors);
            
            if (riskScore >= 0.7) {
                transaction.setStatus(TransactionStatus.FLAGGED);
            }
            
            transactionRepository.save(transaction);
            log.info("Decision made for transaction: {} - Risk score: {}", transaction.getId(), riskScore);
        } catch (Exception e) {
            log.error("Error making decision: {}", transaction.getId(), e);
        }
    }
}

