package com.istream.persistence.entity;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "market_events", indexes = {
        @Index(name = "idx_events_source_asset", columnList = "source, asset"),
        @Index(name = "idx_events_occurred_at",  columnList = "occurred_at DESC"),
        @Index(name = "idx_events_source",        columnList = "source")
})
public class MarketEventEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, length = 50)
    private String source;

    @Column(nullable = false, length = 50)
    private String asset;

    @Column(nullable = false, length = 50)
    private String metric;

    @Column(nullable = false)
    private double value;

    @Column(length = 20)
    private String unit;

    @Column(name = "occurred_at", nullable = false)
    private Instant occurredAt;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt = Instant.now();

    public UUID getId()              { return id; }
    public String getSource()        { return source; }
    public String getAsset()         { return asset; }
    public String getMetric()        { return metric; }
    public double getValue()         { return value; }
    public String getUnit()          { return unit; }
    public Instant getOccurredAt()   { return occurredAt; }
    public Instant getCreatedAt()    { return createdAt; }

    public void setSource(String source)         { this.source = source; }
    public void setAsset(String asset)           { this.asset = asset; }
    public void setMetric(String metric)         { this.metric = metric; }
    public void setValue(double value)           { this.value = value; }
    public void setUnit(String unit)             { this.unit = unit; }
    public void setOccurredAt(Instant occurredAt){ this.occurredAt = occurredAt; }
}
