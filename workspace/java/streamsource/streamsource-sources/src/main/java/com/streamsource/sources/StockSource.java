package com.streamsource.sources;

import com.streamsource.core.model.MarketEvent;
import com.streamsource.core.source.DataSource;
import com.streamsource.sources.config.SourceProperties;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
@ConditionalOnProperty(prefix = "sources.stocks", name = "enabled", havingValue = "true")
public class StockSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(StockSource.class);
    private static final String YAHOO_URL =
            "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d";

    private final RestTemplate restTemplate;
    private final SourceProperties.StockConfig config;
    private List<MarketEvent> lastKnown = List.of();

    public StockSource(RestTemplate restTemplate, SourceProperties sourceProperties) {
        this.restTemplate = restTemplate;
        this.config = sourceProperties.stocks();
    }

    @Override
    public String sourceId() {
        return "stocks";
    }

    @Override
    @CircuitBreaker(name = "stock-source", fallbackMethod = "fetchFallback")
    @Retry(name = "stock-source")
    public List<MarketEvent> fetch() {
        List<MarketEvent> events = new ArrayList<>();

        for (String asset : config.assets()) {
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(YAHOO_URL, Map.class, asset);
                double price = extractPrice(response);
                if (price > 0) {
                    events.add(MarketEvent.builder()
                            .source(sourceId())
                            .asset(asset)
                            .metric("price")
                            .value(price)
                            .unit("USD")
                            .build());
                }
            } catch (Exception e) {
                log.warn("Failed to fetch stock price for {}: {}", asset, e.getMessage());
            }
        }

        lastKnown = events;
        return events;
    }

    @SuppressWarnings("unchecked")
    private double extractPrice(Map<String, Object> response) {
        try {
            Map<String, Object> chart = (Map<String, Object>) response.get("chart");
            List<Map<String, Object>> result = (List<Map<String, Object>>) chart.get("result");
            Map<String, Object> meta = (Map<String, Object>) result.get(0).get("meta");
            return ((Number) meta.get("regularMarketPrice")).doubleValue();
        } catch (Exception e) {
            return 0.0;
        }
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("Stock API circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
