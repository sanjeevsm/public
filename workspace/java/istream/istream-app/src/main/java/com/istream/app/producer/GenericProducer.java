package com.istream.app.producer;

import com.istream.core.model.MarketEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class GenericProducer {

    private static final Logger log = LoggerFactory.getLogger(GenericProducer.class);

    private final KafkaTemplate<String, MarketEvent> kafkaTemplate;

    @Value("${kafka.topics.market-events}")
    private String topic;

    public GenericProducer(KafkaTemplate<String, MarketEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void send(MarketEvent event) {
        String key = event.source() + ":" + event.asset();
        kafkaTemplate.send(topic, key, event).whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Failed to send event [{}]: {}", key, ex.getMessage());
            } else {
                log.debug("Sent [{}] to partition {}", key, result.getRecordMetadata().partition());
            }
        });
    }
}
