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
                                                request.getPassword()));

                User user = userRepository.findByEmail(request.getEmail())
                                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

                String jwtToken = jwtService.generateToken(
                                org.springframework.security.core.userdetails.User.builder()
                                                .username(user.getEmail())
                                                .password(user.getHashedPassword())
                                                .authorities("ROLE_" + user.getRole().name())
                                                .build());

                return AuthResponse.builder()
                                .accessToken(jwtToken)
                                .build();
        }

        public AuthResponse signup(com.fraudmonitoring.dto.SignupRequest request) {
                if (userRepository.existsByEmail(request.getEmail())) {
                        throw new IllegalArgumentException("Email already in use");
                }

                User user = User.builder()
                                .fullName(request.getFullName())
                                .email(request.getEmail())
                                .hashedPassword(passwordEncoder.encode(request.getPassword()))
                                .role(UserRole.EMPLOYEE) // Default role
                                .isActive(true)
                                .build();

                userRepository.save(user);

                String jwtToken = jwtService.generateToken(
                                org.springframework.security.core.userdetails.User.builder()
                                                .username(user.getEmail())
                                                .password(user.getHashedPassword())
                                                .authorities("ROLE_" + user.getRole().name())
                                                .build());

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

        public void createTestUsers() {
                createAdminUser();
                if (!userRepository.existsByEmail("user@example.com")) {
                        User user = User.builder()
                                        .email("user@example.com")
                                        .hashedPassword(passwordEncoder.encode("user123"))
                                        .fullName("Regular User")
                                        .role(UserRole.EMPLOYEE)
                                        .isActive(true)
                                        .build();
                        userRepository.save(user);
                }
        }
}
