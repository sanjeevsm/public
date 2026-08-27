package com.istream.persistence.repository;

import com.istream.persistence.entity.MarketEventEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

public interface MarketEventRepository extends JpaRepository<MarketEventEntity, UUID> {
    Page<MarketEventEntity> findBySource(String source, Pageable pageable);
    Page<MarketEventEntity> findByAsset(String asset, Pageable pageable);
    Page<MarketEventEntity> findBySourceAndAsset(String source, String asset, Pageable pageable);
    Optional<MarketEventEntity> findTopBySourceAndAssetOrderByOccurredAtDesc(String source, String asset);

    @Modifying
    @Query("DELETE FROM MarketEventEntity e WHERE e.source = :source AND e.occurredAt < :cutoff")
    int deleteBySourceAndOccurredAtBefore(@Param("source") String source, @Param("cutoff") Instant cutoff);

    @Modifying
    @Query("DELETE FROM MarketEventEntity e WHERE e.occurredAt < :cutoff")
    int deleteByOccurredAtBefore(@Param("cutoff") Instant cutoff);
}
