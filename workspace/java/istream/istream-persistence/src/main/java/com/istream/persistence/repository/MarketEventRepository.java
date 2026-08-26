package com.istream.persistence.repository;

import com.istream.persistence.entity.MarketEventEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface MarketEventRepository extends JpaRepository<MarketEventEntity, UUID> {
    Page<MarketEventEntity> findBySource(String source, Pageable pageable);
    Page<MarketEventEntity> findByAsset(String asset, Pageable pageable);
    Page<MarketEventEntity> findBySourceAndAsset(String source, String asset, Pageable pageable);
    Optional<MarketEventEntity> findTopBySourceAndAssetOrderByOccurredAtDesc(String source, String asset);
}
