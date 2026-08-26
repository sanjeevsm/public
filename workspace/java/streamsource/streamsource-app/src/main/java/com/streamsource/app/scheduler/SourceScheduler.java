package com.streamsource.app.scheduler;

import com.streamsource.app.producer.GenericProducer;
import com.streamsource.core.source.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class SourceScheduler {

    private static final Logger log = LoggerFactory.getLogger(SourceScheduler.class);

    private final List<DataSource> sources;
    private final GenericProducer producer;

    public SourceScheduler(List<DataSource> sources, GenericProducer producer) {
        this.sources = sources;
        this.producer = producer;
        log.info("SourceScheduler initialized with {} active source(s): {}",
                sources.size(), sources.stream().map(DataSource::sourceId).toList());
    }

    @Scheduled(fixedDelayString = "${pipeline.poll-interval-ms:5000}")
    public void pollAll() {
        sources.parallelStream().forEach(source -> {
            try {
                source.fetch().forEach(producer::send);
            } catch (Exception e) {
                log.error("Error polling source [{}]: {}", source.sourceId(), e.getMessage());
            }
        });
    }
}
