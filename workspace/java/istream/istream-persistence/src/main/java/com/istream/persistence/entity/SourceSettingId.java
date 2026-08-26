package com.istream.persistence.entity;

import java.io.Serializable;
import java.util.Objects;

public class SourceSettingId implements Serializable {
    private String sourceId;
    private String settingKey;

    public SourceSettingId() {}

    public SourceSettingId(String sourceId, String settingKey) {
        this.sourceId = sourceId;
        this.settingKey = settingKey;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof SourceSettingId that)) return false;
        return Objects.equals(sourceId, that.sourceId) && Objects.equals(settingKey, that.settingKey);
    }

    @Override
    public int hashCode() {
        return Objects.hash(sourceId, settingKey);
    }
}
