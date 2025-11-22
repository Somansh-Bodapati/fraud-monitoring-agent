package com.fraudmonitoring.service;

import com.fraudmonitoring.dto.AuthRequest;
import com.fraudmonitoring.dto.AuthResponse;
import com.fraudmonitoring.entity.User;
import com.fraudmonitoring.entity.UserRole;
import com.fraudmonitoring.repository.UserRepository;
import com.fraudmonitoring.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;
    
    public AuthResponse authenticate(AuthRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );
        
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        
        String jwtToken = jwtService.generateToken(
                org.springframework.security.core.userdetails.User.builder()
                        .username(user.getEmail())
                        .password(user.getHashedPassword())
                        .authorities("ROLE_" + user.getRole().name())
                        .build()
        );
        
        return AuthResponse.builder()
                .accessToken(jwtToken)
                .build();
    }
    
    public User register(User user) {
        user.setHashedPassword(passwordEncoder.encode(user.getHashedPassword()));
        return userRepository.save(user);
    }
    
    public void createAdminUser() {
        if (!userRepository.existsByEmail("admin@example.com")) {
            User admin = User.builder()
                    .email("admin@example.com")
                    .hashedPassword(passwordEncoder.encode("admin123"))
                    .fullName("Admin User")
                    .role(UserRole.ADMIN)
                    .isActive(true)
                    .build();
            userRepository.save(admin);
        }
    }
}

