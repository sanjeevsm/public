package com.streamsource.api.controller;

import com.streamsource.api.dto.LoginRequest;
import com.streamsource.api.dto.LoginResponse;
import com.streamsource.api.security.JwtService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@Tag(name = "Authentication", description = "JWT token management")
public class AuthController {

    private final AuthenticationManager authManager;
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    public AuthController(AuthenticationManager authManager, JwtService jwtService,
                          UserDetailsService userDetailsService) {
        this.authManager = authManager;
        this.jwtService = jwtService;
        this.userDetailsService = userDetailsService;
    }

    @PostMapping("/login")
    @Operation(summary = "Authenticate and receive a JWT token")
    public LoginResponse login(@Valid @RequestBody LoginRequest request) {
        authManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.username(), request.password())
        );
        var userDetails = userDetailsService.loadUserByUsername(request.username());
        return new LoginResponse(jwtService.generateToken(userDetails));
    }
}
