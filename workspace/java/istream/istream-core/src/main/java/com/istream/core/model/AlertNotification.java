package com.istream.core.model;

import java.time.Instant;

public record AlertNotification(
        String ruleId,
        String ruleName,
        String source,
        String asset,
        double triggeredValue,
        double threshold,
        String message,
        Instant triggeredAt
) {}
