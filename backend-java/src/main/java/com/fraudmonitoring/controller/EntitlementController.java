package com.fraudmonitoring.controller;

import com.fraudmonitoring.entity.UserRole;
import com.fraudmonitoring.util.AuthUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.*;

@RestController
@RequestMapping("/api/entitlements")
@RequiredArgsConstructor
public class EntitlementController {

    private final AuthUtil authUtil;

    @GetMapping("/actions")
    public ResponseEntity<Map<String, Object>> getEntitledActions() {
        var user = authUtil.getCurrentUser();

        Map<String, Object> entitlements = new HashMap<>();
        boolean isAdmin = user != null && user.getRole() == UserRole.ADMIN;

        Map<String, Boolean> transactionActions = new HashMap<>();
        transactionActions.put("canApprove", isAdmin);
        transactionActions.put("canReject", isAdmin);
        transactionActions.put("canDelete", isAdmin);
        transactionActions.put("canCreate", true);
        transactionActions.put("canView", true);

        entitlements.put("transactions", transactionActions);
        entitlements.put("role", user != null ? user.getRole().name() : "GUEST");

        return ResponseEntity.ok(entitlements);
    }
}
