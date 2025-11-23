package com.fraudmonitoring.controller;

import com.fraudmonitoring.dto.TransactionCreateRequest;
import com.fraudmonitoring.dto.TransactionStatusUpdateRequest;
import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.entity.TransactionStatus;
import com.fraudmonitoring.service.TransactionService;
import com.fraudmonitoring.util.AuthUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;
    private final AuthUtil authUtil;

    @PostMapping
    public ResponseEntity<Transaction> createTransaction(
            @Valid @RequestBody TransactionCreateRequest request) {
        Transaction transaction = transactionService.createTransaction(request, authUtil.getCurrentUser());
        return ResponseEntity.status(HttpStatus.CREATED).body(transaction);
    }

    @GetMapping
    public ResponseEntity<Page<Transaction>> getTransactions(
            Pageable pageable) {
        return ResponseEntity.ok(transactionService.getTransactions(authUtil.getCurrentUser(), pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Transaction> getTransaction(
            @PathVariable Long id) {
        return ResponseEntity.ok(transactionService.getTransaction(id, authUtil.getCurrentUser()));
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<Transaction> updateTransactionStatus(
            @PathVariable Long id,
            @RequestBody TransactionStatusUpdateRequest request) {
        Transaction transaction = transactionService.updateTransactionStatus(id,
                TransactionStatus.valueOf(request.getStatus()), authUtil.getCurrentUser());
        return ResponseEntity.ok(transaction);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTransaction(
            @PathVariable Long id) {
        transactionService.deleteTransaction(id, authUtil.getCurrentUser());
        return ResponseEntity.noContent().build();
    }
}
