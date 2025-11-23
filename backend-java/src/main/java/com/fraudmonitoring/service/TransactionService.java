package com.fraudmonitoring.service;

import com.fraudmonitoring.dto.TransactionCreateRequest;
import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.entity.TransactionStatus;
import com.fraudmonitoring.entity.User;
import com.fraudmonitoring.entity.UserRole;
import com.fraudmonitoring.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final AgentOrchestratorService agentOrchestratorService;

    @Transactional
    public Transaction createTransaction(TransactionCreateRequest request, User user) {
        Transaction transaction = Transaction.builder()
                .user(user)
                .amount(request.getAmount())
                .currency(request.getCurrency())
                .date(request.getDate())
                .description(request.getDescription())
                .merchant(request.getMerchant())
                .category(request.getCategory() != null ? request.getCategory() : "OTHER")
                .source(request.getSource())
                .status(TransactionStatus.PENDING)
                .isAnomaly(false)
                .isReconciled(false)
                .build();

        transaction = transactionRepository.save(transaction);

        // Process through agent system asynchronously
        agentOrchestratorService.processTransaction(transaction);

        return transaction;
    }

    public Page<Transaction> getTransactions(User user, Pageable pageable) {
        if (user.getRole() == UserRole.EMPLOYEE) {
            return transactionRepository.findByUserId(user.getId(), pageable);
        }
        return transactionRepository.findAll(pageable);
    }

    public Transaction getTransaction(Long id, User user) {
        Transaction transaction = transactionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Transaction not found"));

        if (user.getRole() == UserRole.EMPLOYEE && !transaction.getUser().getId().equals(user.getId())) {
            throw new AccessDeniedException("Not authorized to view this transaction");
        }

        return transaction;
    }

    @Transactional
    public Transaction updateTransactionStatus(Long id, TransactionStatus status, User user) {
        if (user.getRole() != UserRole.ADMIN) {
            throw new AccessDeniedException("Only admins can update transaction status");
        }

        Transaction transaction = transactionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Transaction not found"));

        transaction.setStatus(status);
        return transactionRepository.save(transaction);
    }

    @Transactional
    public void deleteTransaction(Long id, User user) {
        if (user.getRole() != UserRole.ADMIN) {
            throw new AccessDeniedException("Only admins can delete transactions");
        }

        Transaction transaction = transactionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Transaction not found"));

        transactionRepository.delete(transaction);
    }
}
