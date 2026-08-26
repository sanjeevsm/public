package com.streamsource.core.notifier;

import com.streamsource.core.model.AlertNotification;

public interface Notifier {
    String notifierId();
    void send(AlertNotification notification);
}
