package com.istream.api.controller;

import com.istream.api.dto.SourceSettingDto;
import com.istream.persistence.service.SourceSettingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/settings")
@Tag(name = "Settings", description = "Runtime source configuration")
public class SettingsController {

    private final SourceSettingService settingService;

    public SettingsController(SourceSettingService settingService) {
        this.settingService = settingService;
    }

    @GetMapping("/sources")
    @Operation(summary = "List all source settings")
    public List<SourceSettingDto> getAllSourceSettings() {
        return settingService.getAll().entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .map(e -> toDto(e.getKey(), e.getValue()))
                .collect(Collectors.toList());
    }

    @GetMapping("/sources/{sourceId}")
    @Operation(summary = "Get settings for a specific source")
    public ResponseEntity<SourceSettingDto> getSourceSettings(@PathVariable String sourceId) {
        Map<String, Map<String, String>> all = settingService.getAll();
        if (!all.containsKey(sourceId)) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(toDto(sourceId, all.get(sourceId)));
    }

    @PutMapping("/sources/{sourceId}")
    @Operation(summary = "Update settings for a specific source")
    public ResponseEntity<SourceSettingDto> updateSourceSettings(
            @PathVariable String sourceId,
            @RequestBody SourceSettingDto dto) {

        Map<String, String> updates = new LinkedHashMap<>(dto.settings());
        updates.put("enabled", String.valueOf(dto.enabled()));
        settingService.updateAll(sourceId, updates);

        return ResponseEntity.ok(toDto(sourceId, settingService.getAll().get(sourceId)));
    }

    private SourceSettingDto toDto(String sourceId, Map<String, String> raw) {
        boolean enabled = Boolean.parseBoolean(raw.getOrDefault("enabled", "false"));
        Map<String, String> settings = raw.entrySet().stream()
                .filter(e -> !e.getKey().equals("enabled"))
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
                        (a, b) -> a, LinkedHashMap::new));
        return new SourceSettingDto(sourceId, enabled, settings);
    }
}
