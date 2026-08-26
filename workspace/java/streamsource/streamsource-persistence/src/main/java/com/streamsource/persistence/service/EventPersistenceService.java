package com.streamsource.persistence.service;

import com.streamsource.core.model.MarketEvent;
import com.streamsource.persistence.entity.MarketEventEntity;
import com.streamsource.persistence.repository.MarketEventRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class EventPersistenceService {

    private final MarketEventRepository repository;

    public EventPersistenceService(MarketEventRepository repository) {
        this.repository = repository;
    }

    @KafkaListener(
            topics = "${kafka.topics.market-events}",
            groupId = "persistence-group",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void persist(MarketEvent event) {
        MarketEventEntity entity = new MarketEventEntity();
        entity.setSource(event.source());
        entity.setAsset(event.asset());
        entity.setMetric(event.metric());
        entity.setValue(event.value());
        entity.setUnit(event.unit());
        entity.setOccurredAt(event.timestamp());
        repository.save(entity);
    }
}
