package com.streamsource.api.dto;

public record LoginResponse(String token, String type, long expiresInMs) {
    public LoginResponse(String token) {
        this(token, "Bearer", 86400000L);
    }
}
