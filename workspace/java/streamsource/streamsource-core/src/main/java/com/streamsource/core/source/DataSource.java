package com.streamsource.core.source;

import com.streamsource.core.model.MarketEvent;

import java.util.List;

public interface DataSource {
    String sourceId();
    List<MarketEvent> fetch();
}
