package com.istream.core.notifier;

import com.istream.core.model.AlertNotification;

public interface Notifier {
    String notifierId();
    void send(AlertNotification notification);
}
