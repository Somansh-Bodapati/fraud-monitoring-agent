package com.fraudmonitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "feedback")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Feedback {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transaction_id")
    private Transaction transaction;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "alert_id")
    private Alert alert;
    
    @Column(name = "feedback_type", nullable = false)
    private String feedbackType;
    
    @Column(name = "original_value", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> originalValue;
    
    @Column(name = "corrected_value", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> correctedValue;
    
    @Column(columnDefinition = "TEXT")
    private String comment;
    
    @Column(name = "is_processed")
    private Boolean isProcessed = false;
    
    @Column(name = "processed_at")
    private LocalDateTime processedAt;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

