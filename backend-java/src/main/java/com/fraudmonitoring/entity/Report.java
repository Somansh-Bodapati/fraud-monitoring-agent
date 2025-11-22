package com.fraudmonitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "reports")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Report {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "report_type", nullable = false)
    private String reportType;
    
    @Column(name = "start_date", nullable = false)
    private LocalDateTime startDate;
    
    @Column(name = "end_date", nullable = false)
    private LocalDateTime endDate;
    
    @Column(columnDefinition = "TEXT")
    private String summary;
    
    @Column(columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> insights;
    
    @Column(columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> statistics;
    
    @Column(name = "generated_by_agent")
    private Boolean generatedByAgent = true;
    
    @Column(name = "generation_metadata", columnDefinition = "TEXT")
    @Convert(converter = JsonConverter.class)
    private Map<String, Object> generationMetadata;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

