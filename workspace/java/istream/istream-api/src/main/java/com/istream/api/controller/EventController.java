package com.istream.api.controller;

import com.istream.persistence.entity.MarketEventEntity;
import com.istream.persistence.repository.MarketEventRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/events")
@Tag(name = "Market Events", description = "Query persisted market events")
public class EventController {

    private final MarketEventRepository repository;

    public EventController(MarketEventRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    @Operation(summary = "List events with optional source/asset filtering and pagination")
    public Page<MarketEventEntity> getEvents(
            @RequestParam(required = false) String source,
            @RequestParam(required = false) String asset,
            Pageable pageable) {

        if (source != null && asset != null) return repository.findBySourceAndAsset(source, asset, pageable);
        if (source != null)                  return repository.findBySource(source, pageable);
        if (asset  != null)                  return repository.findByAsset(asset, pageable);
        return repository.findAll(pageable);
    }

    @GetMapping("/latest/{source}/{asset}")
    @Operation(summary = "Get the most recent event for a given source and asset")
    public MarketEventEntity getLatest(@PathVariable String source, @PathVariable String asset) {
        return repository.findTopBySourceAndAssetOrderByOccurredAtDesc(source, asset)
                .orElseThrow(() -> new RuntimeException("No events found for " + source + "/" + asset));
    }
}
