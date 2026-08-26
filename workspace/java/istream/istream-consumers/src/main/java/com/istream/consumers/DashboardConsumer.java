package com.istream.consumers;

import com.istream.core.model.MarketEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

@Service
public class DashboardConsumer {

    private static final Logger log = LoggerFactory.getLogger(DashboardConsumer.class);

    private final SimpMessagingTemplate wsTemplate;

    public DashboardConsumer(SimpMessagingTemplate wsTemplate) {
        this.wsTemplate = wsTemplate;
    }

    @KafkaListener(
            topics = "${kafka.topics.market-events}",
            groupId = "dashboard-group",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void onEvent(MarketEvent event) {
        wsTemplate.convertAndSend("/topic/events/" + event.source(), event);
        wsTemplate.convertAndSend("/topic/events/all", event);
        log.debug("WebSocket push: {}/{} = {} {}", event.source(), event.asset(), event.value(), event.unit());
    }
}
