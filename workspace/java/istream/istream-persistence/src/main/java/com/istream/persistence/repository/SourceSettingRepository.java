package com.istream.persistence.repository;

import com.istream.persistence.entity.SourceSettingEntity;
import com.istream.persistence.entity.SourceSettingId;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SourceSettingRepository extends JpaRepository<SourceSettingEntity, SourceSettingId> {
    List<SourceSettingEntity> findBySourceId(String sourceId);
}
