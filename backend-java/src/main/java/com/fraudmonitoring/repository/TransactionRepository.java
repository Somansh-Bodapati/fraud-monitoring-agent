package com.fraudmonitoring.repository;

import com.fraudmonitoring.entity.Transaction;
import com.fraudmonitoring.entity.TransactionStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    Page<Transaction> findByUserId(Long userId, Pageable pageable);
    
    @Query("SELECT t FROM Transaction t WHERE t.user.id = :userId " +
           "AND (:status IS NULL OR t.status = :status) " +
           "AND (:category IS NULL OR t.category = :category) " +
           "AND (:isAnomaly IS NULL OR t.isAnomaly = :isAnomaly)")
    Page<Transaction> findByUserIdWithFilters(
        @Param("userId") Long userId,
        @Param("status") TransactionStatus status,
        @Param("category") String category,
        @Param("isAnomaly") Boolean isAnomaly,
        Pageable pageable
    );
    
    List<Transaction> findByUserIdAndDateBetween(
        Long userId, 
        LocalDateTime startDate, 
        LocalDateTime endDate
    );
    
    List<Transaction> findByUserIdAndCategoryAndDateAfter(
        Long userId, 
        String category, 
        LocalDateTime date
    );
}

