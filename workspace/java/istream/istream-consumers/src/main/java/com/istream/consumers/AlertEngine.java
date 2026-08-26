package com.istream.consumers;

import com.istream.core.alert.AlertRule;
import com.istream.core.model.AlertNotification;
import com.istream.core.model.MarketEvent;
import com.istream.core.notifier.Notifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AlertEngine {

    private static final Logger log = LoggerFactory.getLogger(AlertEngine.class);

    private final List<AlertRule> alertRules;
    private final List<Notifier> notifiers;

    public AlertEngine(List<AlertRule> alertRules, List<Notifier> notifiers) {
        this.alertRules = alertRules;
        this.notifiers = notifiers;
    }

    @KafkaListener(
            topics = "${kafka.topics.market-events}",
            groupId = "alert-engine-group",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void process(MarketEvent event) {
        alertRules.stream()
                .filter(rule -> rule.matches(event))
                .map(rule -> rule.buildNotification(event))
                .forEach(this::dispatchToAll);
    }

    private void dispatchToAll(AlertNotification notification) {
        log.info("Alert triggered: [{}] {} = {} (threshold: {})",
                notification.ruleName(), notification.asset(),
                notification.triggeredValue(), notification.threshold());

        notifiers.forEach(notifier -> {
            try {
                notifier.send(notification);
            } catch (Exception e) {
                log.error("Notifier [{}] failed: {}", notifier.notifierId(), e.getMessage());
            }
        });
    }
}
