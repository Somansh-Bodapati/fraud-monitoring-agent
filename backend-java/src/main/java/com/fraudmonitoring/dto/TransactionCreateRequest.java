package com.fraudmonitoring.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class TransactionCreateRequest {
    @NotNull
    @Positive
    private Double amount;
    
    private String currency = "USD";
    
    @NotNull
    private LocalDateTime date;
    
    private String description;
    
    private String merchant;
    
    private String source = "manual";
    
    private Long receiptId;
}

