package com.istream.core.alert;

import com.istream.core.model.AlertNotification;
import com.istream.core.model.MarketEvent;

public interface AlertRule {
    String ruleId();
    boolean matches(MarketEvent event);
    AlertNotification buildNotification(MarketEvent event);
}
