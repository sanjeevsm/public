package com.istream.app;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.istream")
@EntityScan(basePackages = "com.istream.persistence.entity")
@EnableJpaRepositories(basePackages = "com.istream.persistence.repository")
@ConfigurationPropertiesScan(basePackages = "com.istream")
@EnableScheduling
@EnableKafka
@EnableConfigurationProperties
public class IStreamApplication {

    public static void main(String[] args) {
        new SpringApplicationBuilder(IStreamApplication.class)
                .initializers(new LocalKafkaInitializer())
                .run(args);
    }
}
