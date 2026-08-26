package com.streamsource.core.model;

import com.fasterxml.jackson.annotation.JsonFormat;

import java.time.Instant;
import java.util.Map;

public record MarketEvent(
        String source,
        String asset,
        String metric,
        double value,
        String unit,
        @JsonFormat(shape = JsonFormat.Shape.STRING)
        Instant timestamp,
        Map<String, Object> metadata
) {
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String source;
        private String asset;
        private String metric;
        private double value;
        private String unit;
        private Instant timestamp = Instant.now();
        private Map<String, Object> metadata = Map.of();

        public Builder source(String source)   { this.source = source;     return this; }
        public Builder asset(String asset)     { this.asset = asset;       return this; }
        public Builder metric(String metric)   { this.metric = metric;     return this; }
        public Builder value(double value)     { this.value = value;       return this; }
        public Builder unit(String unit)       { this.unit = unit;         return this; }
        public Builder timestamp(Instant ts)   { this.timestamp = ts;      return this; }
        public Builder metadata(Map<String, Object> m) { this.metadata = m; return this; }

        public MarketEvent build() {
            return new MarketEvent(source, asset, metric, value, unit, timestamp, metadata);
        }
    }
}
