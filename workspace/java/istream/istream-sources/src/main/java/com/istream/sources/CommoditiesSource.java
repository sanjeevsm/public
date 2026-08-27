package com.istream.sources;

import com.istream.core.model.MarketEvent;
import com.istream.core.source.DataSource;
import com.istream.core.source.SourceSettingProvider;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Fetches commodity futures prices via Yahoo Finance v8 chart API (no auth required).
 * Default symbols: GC=F (Gold), SI=F (Silver), CL=F (Crude Oil), NG=F (Nat Gas)
 */
@Component
public class CommoditiesSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(CommoditiesSource.class);
    private static final String YAHOO_URL =
            "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d";

    private final RestTemplate restTemplate;
    private final SourceSettingProvider settings;
    private List<MarketEvent> lastKnown = List.of();

    public CommoditiesSource(RestTemplate restTemplate, SourceSettingProvider settings) {
        this.restTemplate = restTemplate;
        this.settings = settings;
    }

    @Override
    public String sourceId() {
        return "commodities";
    }

    @Override
    @CircuitBreaker(name = "commodities-source", fallbackMethod = "fetchFallback")
    public List<MarketEvent> fetch() {
        List<MarketEvent> events = new ArrayList<>();

        for (String symbol : settings.getList(sourceId(), "assets")) {
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(YAHOO_URL, Map.class, symbol);
                double price = extractPrice(response);
                if (price > 0) {
                    events.add(MarketEvent.builder()
                            .source(sourceId())
                            .asset(symbol)
                            .metric("price")
                            .value(price)
                            .unit("USD")
                            .build());
                }
            } catch (Exception e) {
                log.warn("Failed to fetch commodity price for {}: {}", symbol, e.getMessage());
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
        log.warn("Commodities circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
