package com.istream.api.controller;

import com.istream.core.source.DataSource;
import com.istream.core.source.SourceSettingProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/sources")
@Tag(name = "Sources", description = "Active data source registry")
public class SourceController {

    private final List<DataSource> sources;
    private final SourceSettingProvider settingProvider;

    public SourceController(List<DataSource> sources, SourceSettingProvider settingProvider) {
        this.sources = sources;
        this.settingProvider = settingProvider;
    }

    @GetMapping
    @Operation(summary = "List all data sources with their current status")
    public List<Map<String, String>> getActiveSources() {
        return sources.stream()
                .map(s -> Map.of(
                        "id", s.sourceId(),
                        "status", settingProvider.isEnabled(s.sourceId()) ? "active" : "disabled"
                ))
                .collect(Collectors.toList());
    }
}
