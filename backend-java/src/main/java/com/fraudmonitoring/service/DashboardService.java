package com.fraudmonitoring.service;

import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.entity.User;
import com.fraudmonitoring.entity.UserRole;
import com.fraudmonitoring.repository.TransactionRepository;
import com.fraudmonitoring.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DashboardService {

        private final TransactionRepository transactionRepository;
        private final AlertRepository alertRepository;

        @org.springframework.cache.annotation.Cacheable(value = "dashboardStats", key = "#user.id")
        public Map<String, Object> getStats(User user) {
                LocalDateTime cutoffDate = LocalDateTime.now().minusDays(30);

                List<Transaction> transactions;
                if (user.getRole() == UserRole.EMPLOYEE) {
                        transactions = transactionRepository.findByUserIdAndDateBetween(
                                        user.getId(), cutoffDate, LocalDateTime.now());
                } else {
                        transactions = transactionRepository.findAll().stream()
                                        .filter(t -> t.getDate().isAfter(cutoffDate))
                                        .collect(Collectors.toList());
                }

                int totalCount = transactions.size();
                double totalAmount = transactions.stream()
                                .mapToDouble(Transaction::getAmount)
                                .sum();
                long anomalyCount = transactions.stream()
                                .filter(t -> t.getIsAnomaly() != null && t.getIsAnomaly())
                                .count();
                long flaggedCount = transactions.stream()
                                .filter(t -> t.getStatus().name().equals("FLAGGED"))
                                .count();

                // Category breakdown
                Map<String, Map<String, Object>> categoryBreakdown = transactions.stream()
                                .filter(t -> t.getCategory() != null)
                                .collect(Collectors.groupingBy(
                                                Transaction::getCategory,
                                                Collectors.collectingAndThen(
                                                                Collectors.toList(),
                                                                list -> {
                                                                        Map<String, Object> stats = new HashMap<>();
                                                                        stats.put("count", list.size());
                                                                        stats.put("total", list.stream()
                                                                                        .mapToDouble(Transaction::getAmount)
                                                                                        .sum());
                                                                        return stats;
                                                                })));

                // Alerts
                long alertCount = alertRepository.count();
                long unreadAlerts = alertRepository.findAll().stream()
                                .filter(a -> !a.getIsRead())
                                .count();

                Map<String, Object> result = new HashMap<>();
                result.put("transactions", Map.of(
                                "total", totalCount,
                                "totalAmount", totalAmount,
                                "anomalies", anomalyCount,
                                "flagged", flaggedCount));
                result.put("alerts", Map.of(
                                "total", alertCount,
                                "unread", unreadAlerts));
                result.put("categoryBreakdown", categoryBreakdown);

                return result;
        }
}
