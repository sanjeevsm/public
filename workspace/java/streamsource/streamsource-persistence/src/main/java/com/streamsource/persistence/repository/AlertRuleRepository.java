package com.streamsource.persistence.repository;

import com.streamsource.persistence.entity.AlertRuleEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface AlertRuleRepository extends JpaRepository<AlertRuleEntity, UUID> {
    List<AlertRuleEntity> findByActiveTrue();
    List<AlertRuleEntity> findBySourceAndAsset(String source, String asset);
}
