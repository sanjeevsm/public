package com.istream.persistence.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "source_settings")
@IdClass(SourceSettingId.class)
public class SourceSettingEntity {

    @Id
    @Column(name = "source_id", nullable = false, length = 50)
    private String sourceId;

    @Id
    @Column(name = "setting_key", nullable = false, length = 100)
    private String settingKey;

    @Column(name = "setting_value", nullable = false)
    private String settingValue = "";

    @Column(name = "updated_at")
    private Instant updatedAt = Instant.now();

    public SourceSettingEntity() {}

    public SourceSettingEntity(String sourceId, String settingKey, String settingValue) {
        this.sourceId = sourceId;
        this.settingKey = settingKey;
        this.settingValue = settingValue;
        this.updatedAt = Instant.now();
    }

    public String getSourceId()      { return sourceId; }
    public String getSettingKey()    { return settingKey; }
    public String getSettingValue()  { return settingValue; }
    public Instant getUpdatedAt()    { return updatedAt; }

    public void setSettingValue(String settingValue) {
        this.settingValue = settingValue;
        this.updatedAt = Instant.now();
    }
}
