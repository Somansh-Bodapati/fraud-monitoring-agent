package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

@Service
@Slf4j
public class OpenAIService {
    
    @Value("${app.openai.api-key:}")
    private String apiKey;
    
    @Value("${app.openai.model:gpt-4-turbo-preview}")
    private String model;
    
    private static final List<String> CATEGORIES = Arrays.asList(
            "travel", "meals", "subscription", "office_supplies", "software",
            "utilities", "marketing", "professional_services", "equipment",
            "rent", "insurance", "training", "entertainment", "transportation", "other"
    );
    
    public String classifyTransaction(Transaction transaction) {
        // Simplified classification - in production, use OpenAI API
        if (apiKey.isEmpty()) {
            // Fallback to simple rule-based classification
            String merchant = transaction.getMerchant() != null 
                    ? transaction.getMerchant().toLowerCase() 
                    : "";
            String description = transaction.getDescription() != null 
                    ? transaction.getDescription().toLowerCase() 
                    : "";
            
            if (merchant.contains("starbucks") || merchant.contains("restaurant") || 
                description.contains("lunch") || description.contains("dinner")) {
                return "meals";
            } else if (merchant.contains("uber") || merchant.contains("lyft") || 
                      description.contains("taxi") || description.contains("transport")) {
                return "transportation";
            } else if (merchant.contains("hotel") || merchant.contains("airline") || 
                      description.contains("flight") || description.contains("hotel")) {
                return "travel";
            } else {
                return "other";
            }
        }
        
        // TODO: Implement actual OpenAI API call
        return "other";
    }
}

