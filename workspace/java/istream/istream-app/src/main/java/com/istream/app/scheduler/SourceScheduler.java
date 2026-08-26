package com.istream.app.scheduler;

import com.istream.app.producer.GenericProducer;
import com.istream.core.source.DataSource;
import com.istream.core.source.SourceSettingProvider;
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
    private final SourceSettingProvider settings;

    public SourceScheduler(List<DataSource> sources, GenericProducer producer, SourceSettingProvider settings) {
        this.sources = sources;
        this.producer = producer;
        this.settings = settings;
        log.info("SourceScheduler initialized with {} source(s): {}",
                sources.size(), sources.stream().map(DataSource::sourceId).toList());
    }

    @Scheduled(fixedDelayString = "${pipeline.poll-interval-ms:5000}")
    public void pollAll() {
        sources.parallelStream()
                .filter(s -> settings.isEnabled(s.sourceId()))
                .forEach(source -> {
                    try {
                        source.fetch().forEach(producer::send);
                    } catch (Exception e) {
                        log.error("Error polling source [{}]: {}", source.sourceId(), e.getMessage());
                    }
                });
    }
}
