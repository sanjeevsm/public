CREATE TABLE source_settings (
    source_id     VARCHAR(50)  NOT NULL,
    setting_key   VARCHAR(100) NOT NULL,
    setting_value TEXT         NOT NULL DEFAULT '',
    updated_at    TIMESTAMPTZ  DEFAULT NOW(),
    PRIMARY KEY (source_id, setting_key)
);

INSERT INTO source_settings (source_id, setting_key, setting_value) VALUES
  ('crypto',  'enabled',   'true'),
  ('crypto',  'assets',    'BTC-USD,ETH-USD,SOL-USD'),
  ('crypto',  'currency',  'usd'),
  ('crypto',  'intervalMs','30000'),
  ('stocks',  'enabled',   'true'),
  ('stocks',  'assets',    'AAPL,TSLA,MSFT'),
  ('stocks',  'intervalMs','30000'),
  ('weather', 'enabled',   'false'),
  ('weather', 'cities',    'London,New York'),
  ('weather', 'apiKey',    ''),
  ('weather', 'intervalMs','30000');
