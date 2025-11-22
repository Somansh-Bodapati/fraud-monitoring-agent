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
@Table(name = "receipts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Receipt {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transaction_id")
    private Transaction transaction;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "file_path", nullable = false)
    private String filePath;
    
    @Column(name = "file_name", nullable = false)
    private String fileName;
    
    @Column(name = "file_type")
    private String fileType;
    
    private Double amount;
    
    private LocalDateTime date;
    
    private String merchant;
    
    private String category;
    
    @Column(name = "line_items", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private List<Map<String, Object>> lineItems;
    
    private Double tax;
    
    private Double total;
    
    @Column(name = "parsing_confidence")
    private Double parsingConfidence;
    
    @Column(name = "parsing_metadata", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> parsingMetadata;
    
    @Column(name = "raw_text", columnDefinition = "TEXT")
    private String rawText;
    
    @Column(name = "is_processed")
    private Boolean isProcessed = false;
    
    @Column(name = "is_verified")
    private Boolean isVerified = false;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
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

