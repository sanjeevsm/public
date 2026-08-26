package com.istream.app;

import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.event.ContextClosedEvent;
import org.springframework.core.env.MapPropertySource;
import org.springframework.kafka.test.EmbeddedKafkaBroker;
import org.springframework.kafka.test.EmbeddedKafkaKraftBroker;

import java.util.Arrays;
import java.util.Map;

/**
 * Starts an in-process KRaft Kafka broker when the "local" Spring profile is active.
 * Runs before any Spring beans are created so that the bootstrap-servers property
 * is visible to KafkaAdmin / producer / consumer factories on startup.
 */
public class LocalKafkaInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    private static final int BROKER_PORT = 9092;

    @Override
    public void initialize(ConfigurableApplicationContext context) {
        if (!Arrays.asList(context.getEnvironment().getActiveProfiles()).contains("local")) {
            return;
        }

        EmbeddedKafkaBroker broker = new EmbeddedKafkaKraftBroker(1, 3,
                "istream.market.events")
                .kafkaPorts(BROKER_PORT);
        try {
            broker.afterPropertiesSet();
        } catch (Exception e) {
            throw new IllegalStateException("Embedded Kafka (KRaft) failed to start on port " + BROKER_PORT, e);
        }

        // Use the address the broker actually bound to (may differ from the requested port)
        String bootstrapServers = broker.getBrokersAsString();
        context.getEnvironment().getPropertySources().addFirst(
                new MapPropertySource("embeddedKafka",
                        Map.of("spring.kafka.bootstrap-servers", bootstrapServers)));

        context.addApplicationListener(event -> {
            if (event instanceof ContextClosedEvent) {
                broker.destroy();
            }
        });
    }
}
