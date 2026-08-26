package com.streamsource.api.controller;

import com.streamsource.core.source.DataSource;
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

    public SourceController(List<DataSource> sources) {
        this.sources = sources;
    }

    @GetMapping
    @Operation(summary = "List all active data sources")
    public List<Map<String, String>> getActiveSources() {
        return sources.stream()
                .map(s -> Map.of("id", s.sourceId(), "status", "active"))
                .collect(Collectors.toList());
    }
}
