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
import java.util.stream.Collectors;

@Component
public class CryptoSource implements DataSource {

    private static final Logger log = LoggerFactory.getLogger(CryptoSource.class);
    private static final String BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbols=";

    private static final Map<String, String> ASSET_TO_SYMBOL = Map.of(
            "BTC-USD", "BTCUSDT",
            "ETH-USD", "ETHUSDT",
            "SOL-USD", "SOLUSDT",
            "BNB-USD", "BNBUSDT",
            "XRP-USD", "XRPUSDT",
            "ADA-USD", "ADAUSDT"
    );
    private static final Map<String, String> SYMBOL_TO_ASSET = Map.of(
            "BTCUSDT", "BTC-USD",
            "ETHUSDT", "ETH-USD",
            "SOLUSDT", "SOL-USD",
            "BNBUSDT", "BNB-USD",
            "XRPUSDT", "XRP-USD",
            "ADAUSDT", "ADA-USD"
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

        String symbolsJson = assets.stream()
                .map(a -> ASSET_TO_SYMBOL.getOrDefault(a, a.replace("-USD", "USDT")))
                .map(s -> "\"" + s + "\"")
                .collect(Collectors.joining(",", "[", "]"));

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> tickers = restTemplate.getForObject(
                BINANCE_URL + symbolsJson, List.class
        );

        if (tickers == null) return List.of();

        List<MarketEvent> events = new ArrayList<>();
        for (Map<String, Object> ticker : tickers) {
            String symbol = (String) ticker.get("symbol");
            String asset = SYMBOL_TO_ASSET.getOrDefault(symbol, symbol);
            double price = Double.parseDouble((String) ticker.get("price"));
            events.add(MarketEvent.builder()
                    .source(sourceId())
                    .asset(asset)
                    .metric("price")
                    .value(price)
                    .unit("USDT")
                    .build());
        }

        lastKnown = events;
        return events;
    }

    public List<MarketEvent> fetchFallback(Exception e) {
        log.warn("Binance circuit open, using cached data: {}", e.getMessage());
        return lastKnown;
    }
}
