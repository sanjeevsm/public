package com.istream.core.source;

import com.istream.core.model.MarketEvent;

import java.util.List;

public interface DataSource {
    String sourceId();
    List<MarketEvent> fetch();
}
