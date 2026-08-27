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
import java.util.concurrent.ConcurrentHashMap;

@Component
public class WeatherSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(WeatherSource.class);
    private static final String GEOCODE_URL =
            "https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json";
    private static final String FORECAST_URL =
            "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}" +
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=auto";

    private final RestTemplate restTemplate;
    private final SourceSettingProvider settings;
    private final Map<String, double[]> coordCache = new ConcurrentHashMap<>();
    private List<MarketEvent> lastKnown = List.of();

    public WeatherSource(RestTemplate restTemplate, SourceSettingProvider settings) {
        this.restTemplate = restTemplate;
        this.settings = settings;
    }

    @Override
    public String sourceId() {
        return "weather";
    }

    @Override
    @CircuitBreaker(name = "weather-source", fallbackMethod = "fetchFallback")
    public List<MarketEvent> fetch() {
        List<MarketEvent> events = new ArrayList<>();

        for (String city : settings.getList(sourceId(), "cities")) {
            try {
                double[] coords = resolveCoords(city);
                if (coords == null) {
                    log.warn("Could not geocode city: {}", city);
                    continue;
                }

                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(
                        FORECAST_URL, Map.class, coords[0], coords[1]);

                if (response == null) continue;

                @SuppressWarnings("unchecked")
                Map<String, Object> current = (Map<String, Object>) response.get("current");
                if (current == null) continue;

                double temp     = ((Number) current.get("temperature_2m")).doubleValue();
                double humidity = ((Number) current.get("relative_humidity_2m")).doubleValue();
                double wind     = ((Number) current.get("wind_speed_10m")).doubleValue();

                events.add(MarketEvent.builder()
                        .source(sourceId()).asset(city)
                        .metric("temperature").value(temp).unit("Celsius").build());
                events.add(MarketEvent.builder()
                        .source(sourceId()).asset(city)
                        .metric("humidity").value(humidity).unit("percent").build());
                events.add(MarketEvent.builder()
                        .source(sourceId()).asset(city)
                        .metric("wind_speed").value(wind).unit("km/h").build());

            } catch (Exception e) {
                log.warn("Failed to fetch weather for {}: {}", city, e.getMessage());
            }
        }

        lastKnown = events;
        return events;
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("Weather circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }

    @SuppressWarnings("unchecked")
    private double[] resolveCoords(String city) {
        double[] cached = coordCache.get(city);
        if (cached != null) return cached;

        try {
            Map<String, Object> resp = restTemplate.getForObject(GEOCODE_URL, Map.class, city);
            if (resp == null) return null;
            List<Map<String, Object>> results = (List<Map<String, Object>>) resp.get("results");
            if (results == null || results.isEmpty()) return null;
            Map<String, Object> loc = results.get(0);
            double lat = ((Number) loc.get("latitude")).doubleValue();
            double lon = ((Number) loc.get("longitude")).doubleValue();
            double[] coords = {lat, lon};
            coordCache.put(city, coords);
            return coords;
        } catch (Exception e) {
            log.warn("Geocoding failed for {}: {}", city, e.getMessage());
            return null;
        }
    }
}
