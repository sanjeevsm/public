package com.istream.core.source;

import java.util.List;

public interface SourceSettingProvider {
    boolean isEnabled(String sourceId);
    String get(String sourceId, String key, String defaultValue);
    List<String> getList(String sourceId, String key);
}
