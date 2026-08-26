package com.istream.persistence.service;

import com.istream.core.source.SourceSettingProvider;
import com.istream.persistence.entity.SourceSettingEntity;
import com.istream.persistence.entity.SourceSettingId;
import com.istream.persistence.repository.SourceSettingRepository;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class SourceSettingService implements SourceSettingProvider {

    private final SourceSettingRepository repo;
    private final Map<String, Map<String, String>> cache = new ConcurrentHashMap<>();

    public SourceSettingService(SourceSettingRepository repo) {
        this.repo = repo;
    }

    @PostConstruct
    public void loadCache() {
        cache.clear();
        repo.findAll().forEach(e ->
            cache.computeIfAbsent(e.getSourceId(), k -> new ConcurrentHashMap<>())
                 .put(e.getSettingKey(), e.getSettingValue())
        );
    }

    @Override
    public boolean isEnabled(String sourceId) {
        return Boolean.parseBoolean(get(sourceId, "enabled", "false"));
    }

    @Override
    public String get(String sourceId, String key, String defaultValue) {
        return cache.getOrDefault(sourceId, Map.of()).getOrDefault(key, defaultValue);
    }

    @Override
    public List<String> getList(String sourceId, String key) {
        String val = get(sourceId, key, "");
        if (val.isBlank()) return List.of();
        return Arrays.stream(val.split(","))
                     .map(String::trim)
                     .filter(s -> !s.isEmpty())
                     .collect(Collectors.toList());
    }

    public Map<String, Map<String, String>> getAll() {
        return Collections.unmodifiableMap(
            cache.entrySet().stream()
                 .collect(Collectors.toMap(Map.Entry::getKey, e -> new LinkedHashMap<>(e.getValue())))
        );
    }

    @Transactional
    public void updateAll(String sourceId, Map<String, String> settings) {
        settings.forEach((key, value) -> {
            SourceSettingEntity entity = repo.findById(new SourceSettingId(sourceId, key))
                    .orElseGet(() -> new SourceSettingEntity(sourceId, key, ""));
            entity.setSettingValue(value != null ? value : "");
            repo.save(entity);
            cache.computeIfAbsent(sourceId, k -> new ConcurrentHashMap<>()).put(key, value != null ? value : "");
        });
    }
}
