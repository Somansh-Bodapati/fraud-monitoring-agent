package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnomalyAgentService {
    
    private final TransactionRepository transactionRepository;
    
    @Value("${app.agent.anomaly-threshold:2.0}")
    private Double anomalyThreshold;
    
    public void detectAnomalies(Transaction transaction) {
        try {
            // Get historical transactions
            LocalDateTime cutoffDate = LocalDateTime.now().minusDays(90);
            List<Transaction> historical = transactionRepository.findByUserIdAndCategoryAndDateAfter(
                    transaction.getUser().getId(),
                    transaction.getCategory(),
                    cutoffDate
            );
            
            if (historical.isEmpty()) {
                return;
            }
            
            // Calculate Z-score
            DescriptiveStatistics stats = new DescriptiveStatistics();
            historical.forEach(t -> stats.addValue(t.getAmount()));
            
            double mean = stats.getMean();
            double std = stats.getStandardDeviation();
            
            if (std > 0) {
                double zScore = Math.abs((transaction.getAmount() - mean) / std);
                
                if (zScore > anomalyThreshold) {
                    transaction.setIsAnomaly(true);
                    transaction.setAnomalyScore(zScore);
                    transaction.setAnomalyReason(String.format(
                            "Amount $%.2f is significantly different from average $%.2f (Z-score: %.2f)",
                            transaction.getAmount(), mean, zScore
                    ));
                    transactionRepository.save(transaction);
                    log.info("Anomaly detected for transaction: {}", transaction.getId());
                }
            }
        } catch (Exception e) {
            log.error("Error detecting anomalies: {}", transaction.getId(), e);
        }
    }
}

