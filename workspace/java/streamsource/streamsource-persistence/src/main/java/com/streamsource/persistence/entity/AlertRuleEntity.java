package com.streamsource.persistence.entity;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "alert_rules")
public class AlertRuleEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 50)
    private String source;

    @Column(nullable = false, length = 50)
    private String asset;

    @Column(nullable = false, length = 50)
    private String metric;

    @Column(nullable = false, length = 10)
    private String condition; // GT, LT, GTE, LTE, EQ

    @Column(nullable = false)
    private double threshold;

    @Column(nullable = false)
    private boolean active = true;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt = Instant.now();

    public UUID getId()            { return id; }
    public String getName()        { return name; }
    public String getSource()      { return source; }
    public String getAsset()       { return asset; }
    public String getMetric()      { return metric; }
    public String getCondition()   { return condition; }
    public double getThreshold()   { return threshold; }
    public boolean isActive()      { return active; }
    public Instant getCreatedAt()  { return createdAt; }

    public void setName(String name)           { this.name = name; }
    public void setSource(String source)       { this.source = source; }
    public void setAsset(String asset)         { this.asset = asset; }
    public void setMetric(String metric)       { this.metric = metric; }
    public void setCondition(String condition) { this.condition = condition; }
    public void setThreshold(double threshold) { this.threshold = threshold; }
    public void setActive(boolean active)      { this.active = active; }
}
