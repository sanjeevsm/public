-- Remove legacy apiKey from weather (Open-Meteo requires none)
DELETE FROM source_settings WHERE source_id = 'weather' AND setting_key = 'apiKey';

-- Forex defaults (open.er-api.com, free, no key)
INSERT INTO source_settings (source_id, setting_key, setting_value) VALUES
  ('forex', 'enabled',      'true'),
  ('forex', 'baseCurrency', 'USD'),
  ('forex', 'pairs',        'USD/EUR,USD/GBP,USD/JPY,USD/CAD,USD/AUD,USD/CHF'),
  ('forex', 'intervalMs',   '60000');

-- Commodities defaults (Yahoo Finance futures, free with User-Agent)
INSERT INTO source_settings (source_id, setting_key, setting_value) VALUES
  ('commodities', 'enabled',    'true'),
  ('commodities', 'assets',     'GC=F,SI=F,CL=F,NG=F'),
  ('commodities', 'intervalMs', '60000');
