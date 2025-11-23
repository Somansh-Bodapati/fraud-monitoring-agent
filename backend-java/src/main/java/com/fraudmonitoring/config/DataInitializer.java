package com.fraudmonitoring.config;

import com.fraudmonitoring.service.AuthService;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class DataInitializer {

    private final AuthService authService;

    @PostConstruct
    public void init() {
        authService.createTestUsers();
    }
}
