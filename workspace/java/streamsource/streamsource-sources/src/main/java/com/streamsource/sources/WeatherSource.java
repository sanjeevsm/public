package com.streamsource.sources;

import com.streamsource.core.model.MarketEvent;
import com.streamsource.core.source.DataSource;
import com.streamsource.sources.config.SourceProperties;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
@ConditionalOnProperty(prefix = "sources.weather", name = "enabled", havingValue = "true")
public class WeatherSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(WeatherSource.class);
    private static final String OPENWEATHER_URL =
            "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&units=metric";

    private final RestTemplate restTemplate;
    private final SourceProperties.WeatherConfig config;
    private List<MarketEvent> lastKnown = List.of();

    public WeatherSource(RestTemplate restTemplate, SourceProperties sourceProperties) {
        this.restTemplate = restTemplate;
        this.config = sourceProperties.weather();
    }

    @Override
    public String sourceId() {
        return "weather";
    }

    @Override
    @CircuitBreaker(name = "weather-source", fallbackMethod = "fetchFallback")
    public List<MarketEvent> fetch() {
        List<MarketEvent> events = new ArrayList<>();

        for (String city : config.cities()) {
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(
                        OPENWEATHER_URL, Map.class, city, config.apiKey()
                );
                if (response != null) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> main = (Map<String, Object>) response.get("main");
                    double temp = ((Number) main.get("temp")).doubleValue();
                    double humidity = ((Number) main.get("humidity")).doubleValue();

                    events.add(MarketEvent.builder()
                            .source(sourceId()).asset(city)
                            .metric("temperature").value(temp).unit("Celsius").build());
                    events.add(MarketEvent.builder()
                            .source(sourceId()).asset(city)
                            .metric("humidity").value(humidity).unit("percent").build());
                }
            } catch (Exception e) {
                log.warn("Failed to fetch weather for {}: {}", city, e.getMessage());
            }
        }

        lastKnown = events;
        return events;
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("Weather API circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
