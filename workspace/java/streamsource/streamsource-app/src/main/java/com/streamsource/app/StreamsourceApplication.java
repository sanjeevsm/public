package com.streamsource.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.streamsource")
@EnableScheduling
@EnableKafka
@EnableConfigurationProperties
public class StreamsourceApplication {

    public static void main(String[] args) {
        SpringApplication.run(StreamsourceApplication.class, args);
    }
}
