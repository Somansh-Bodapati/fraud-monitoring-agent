package com.fraudmonitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "transactions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "external_id", unique = true)
    private String externalId;
    
    @Column(nullable = false)
    private Double amount;
    
    private String currency = "USD";
    
    @Column(nullable = false)
    private LocalDateTime date;
    
    private String description;
    
    private String merchant;
    
    private String category;
    
    private String subcategory;
    
    @Enumerated(EnumType.STRING)
    private TransactionStatus status = TransactionStatus.PENDING;
    
    @Column(name = "is_anomaly")
    private Boolean isAnomaly = false;
    
    @Column(name = "anomaly_score")
    private Double anomalyScore;
    
    @Column(name = "anomaly_reason", columnDefinition = "TEXT")
    private String anomalyReason;
    
    @Column(name = "classification_confidence")
    private Double classificationConfidence;
    
    @Column(name = "classification_metadata", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> classificationMetadata;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "receipt_id")
    private Receipt receipt;
    
    @Column(name = "is_reconciled")
    private Boolean isReconciled = false;
    
    @Column(name = "risk_score")
    private Double riskScore;
    
    @Column(name = "risk_factors", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private List<String> riskFactors;
    
    private String source;
    
    @Column(name = "extra_metadata", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> extraMetadata;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "transaction", cascade = CascadeType.ALL)
    private List<Alert> alerts;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

