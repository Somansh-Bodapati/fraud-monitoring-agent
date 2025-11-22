package com.fraudmonitoring.controller;

import com.fraudmonitoring.entity.Alert;
import com.fraudmonitoring.entity.User;
import com.fraudmonitoring.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/alerts")
@RequiredArgsConstructor
public class AlertController {
    
    private final AlertRepository alertRepository;
    
    @GetMapping
    public ResponseEntity<List<Alert>> getAlerts(
            @AuthenticationPrincipal User user,
            Pageable pageable
    ) {
        if (user.getRole().name().equals("EMPLOYEE")) {
            return ResponseEntity.ok(alertRepository.findByUserId(user.getId(), pageable).getContent());
        }
        return ResponseEntity.ok(alertRepository.findAll(pageable).getContent());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Alert> getAlert(@PathVariable Long id) {
        return ResponseEntity.ok(alertRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Alert not found")));
    }
    
    @PatchMapping("/{id}/read")
    public ResponseEntity<Void> markAsRead(@PathVariable Long id) {
        Alert alert = alertRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Alert not found"));
        alert.setIsRead(true);
        alertRepository.save(alert);
        return ResponseEntity.ok().build();
    }
}

