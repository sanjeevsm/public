package com.istream.api.dto;

import java.util.Map;

public record SourceSettingDto(
        String sourceId,
        boolean enabled,
        Map<String, String> settings
) {}
