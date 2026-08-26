CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE market_events (
    id          UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    source      VARCHAR(50)   NOT NULL,
    asset       VARCHAR(50)   NOT NULL,
    metric      VARCHAR(50)   NOT NULL,
    value       FLOAT8 NOT NULL,
    unit        VARCHAR(20),
    occurred_at TIMESTAMPTZ   NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX idx_events_source_asset ON market_events(source, asset);
CREATE INDEX idx_events_occurred_at  ON market_events(occurred_at DESC);
CREATE INDEX idx_events_source       ON market_events(source);

CREATE TABLE alert_rules (
    id          UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100)  NOT NULL,
    source      VARCHAR(50)   NOT NULL,
    asset       VARCHAR(50)   NOT NULL,
    metric      VARCHAR(50)   NOT NULL,
    condition   VARCHAR(10)   NOT NULL CHECK (condition IN ('GT', 'LT', 'GTE', 'LTE', 'EQ')),
    threshold   FLOAT8 NOT NULL,
    active      BOOLEAN       DEFAULT true,
    created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE TABLE users (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    VARCHAR(50)  UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(20)  DEFAULT 'USER',
    enabled     BOOLEAN      DEFAULT true,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

-- Default admin user: password is 'admin123' — CHANGE IN PRODUCTION
INSERT INTO users (username, password, role)
VALUES ('admin', '$2a$10$m7BX0rorUQjsBWojOAM4QeqxCyA01QxSxtnzvLXVdghmcsXRIpawK', 'ADMIN');
