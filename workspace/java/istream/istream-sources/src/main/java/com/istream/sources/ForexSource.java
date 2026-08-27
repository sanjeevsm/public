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

@Component
public class ForexSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(ForexSource.class);
    private static final String RATES_URL = "https://open.er-api.com/v6/latest/{base}";

    private final RestTemplate restTemplate;
    private final SourceSettingProvider settings;
    private List<MarketEvent> lastKnown = List.of();

    public ForexSource(RestTemplate restTemplate, SourceSettingProvider settings) {
        this.restTemplate = restTemplate;
        this.settings = settings;
    }

    @Override
    public String sourceId() {
        return "forex";
    }

    @Override
    @CircuitBreaker(name = "forex-source", fallbackMethod = "fetchFallback")
    @SuppressWarnings("unchecked")
    public List<MarketEvent> fetch() {
        List<MarketEvent> events = new ArrayList<>();
        String base = settings.get(sourceId(), "baseCurrency", "USD");
        List<String> pairs = settings.getList(sourceId(), "pairs");

        try {
            Map<String, Object> response = restTemplate.getForObject(RATES_URL, Map.class, base);
            if (response == null || !"success".equals(response.get("result"))) {
                log.warn("Forex API returned non-success response");
                return lastKnown;
            }

            Map<String, Object> rates = (Map<String, Object>) response.get("rates");
            if (rates == null) return lastKnown;

            for (String pair : pairs) {
                String[] parts = pair.split("/");
                if (parts.length != 2) continue;
                String quote = parts[1].trim().toUpperCase();
                Object rateObj = rates.get(quote);
                if (rateObj == null) {
                    log.debug("No rate for {}", quote);
                    continue;
                }
                double rate = ((Number) rateObj).doubleValue();
                events.add(MarketEvent.builder()
                        .source(sourceId())
                        .asset(base + "/" + quote)
                        .metric("rate")
                        .value(rate)
                        .unit(quote)
                        .build());
            }
        } catch (Exception e) {
            log.warn("Forex fetch failed: {}", e.getMessage());
        }

        lastKnown = events;
        return events;
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("Forex circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
