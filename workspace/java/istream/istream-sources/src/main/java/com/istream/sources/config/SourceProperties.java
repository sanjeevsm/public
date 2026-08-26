package com.istream.sources.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@ConfigurationProperties(prefix = "sources")
public record SourceProperties(
        CryptoConfig crypto,
        StockConfig stocks,
        WeatherConfig weather
) {
    public record CryptoConfig(boolean enabled, List<String> assets, long intervalMs, String currency) {}
    public record StockConfig(boolean enabled, List<String> assets, long intervalMs) {}
    public record WeatherConfig(boolean enabled, List<String> cities, long intervalMs, String apiKey) {}
}
