package com.streamsource.core.alert;

import com.streamsource.core.model.AlertNotification;
import com.streamsource.core.model.MarketEvent;

public interface AlertRule {
    String ruleId();
    boolean matches(MarketEvent event);
    AlertNotification buildNotification(MarketEvent event);
}
