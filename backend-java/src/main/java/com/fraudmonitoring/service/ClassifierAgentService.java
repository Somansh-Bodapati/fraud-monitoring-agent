package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class ClassifierAgentService {
    
    private final TransactionRepository transactionRepository;
    private final OpenAIService openAIService;
    
    @Value("${app.agent.confidence-threshold:0.7}")
    private Double confidenceThreshold;
    
    public void classifyTransaction(Transaction transaction) {
        try {
            String category = openAIService.classifyTransaction(transaction);
            transaction.setCategory(category);
            transaction.setClassificationConfidence(0.85); // Mock confidence
            transactionRepository.save(transaction);
            log.info("Transaction {} classified as: {}", transaction.getId(), category);
        } catch (Exception e) {
            log.error("Error classifying transaction: {}", transaction.getId(), e);
        }
    }
}

