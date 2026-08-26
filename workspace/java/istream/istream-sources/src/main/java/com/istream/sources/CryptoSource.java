package com.istream.sources;

import com.istream.core.model.MarketEvent;
import com.istream.core.source.DataSource;
import com.istream.core.source.SourceSettingProvider;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
public class CryptoSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(CryptoSource.class);
    private static final String COINGECKO_URL =
            "https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={currency}";

    private static final Map<String, String> ASSET_TO_ID = Map.of(
            "BTC-USD", "bitcoin",
            "ETH-USD", "ethereum",
            "SOL-USD", "solana",
            "BNB-USD", "binancecoin"
    );

    private final RestTemplate restTemplate;
    private final SourceSettingProvider settings;
    private List<MarketEvent> lastKnown = List.of();

    public CryptoSource(RestTemplate restTemplate, SourceSettingProvider settings) {
        this.restTemplate = restTemplate;
        this.settings = settings;
    }

    @Override
    public String sourceId() {
        return "crypto";
    }

    @Override
    @CircuitBreaker(name = "crypto-source", fallbackMethod = "fetchFallback")
    @Retry(name = "crypto-source")
    public List<MarketEvent> fetch() {
        List<String> assets = settings.getList(sourceId(), "assets");
        String currency = settings.get(sourceId(), "currency", "usd");

        String ids = assets.stream()
                .map(a -> ASSET_TO_ID.getOrDefault(a, a.toLowerCase().replace("-usd", "")))
                .reduce((a, b) -> a + "," + b)
                .orElse("bitcoin");

        @SuppressWarnings("unchecked")
        Map<String, Map<String, Double>> response = restTemplate.getForObject(
                COINGECKO_URL, Map.class, ids, currency
        );

        if (response == null) return List.of();

        List<MarketEvent> events = new ArrayList<>();
        assets.forEach(asset -> {
            String coinId = ASSET_TO_ID.getOrDefault(asset, asset.toLowerCase().replace("-usd", ""));
            Map<String, Double> prices = response.get(coinId);
            if (prices != null) {
                events.add(MarketEvent.builder()
                        .source(sourceId())
                        .asset(asset)
                        .metric("price")
                        .value(prices.getOrDefault(currency, 0.0))
                        .unit(currency.toUpperCase())
                        .build());
            }
        });

        lastKnown = events;
        return events;
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("CoinGecko circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
