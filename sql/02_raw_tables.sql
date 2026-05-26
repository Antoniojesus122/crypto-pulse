-- Tabla principal de ingesta: un snapshot por moneda por hora
CREATE TABLE IF NOT EXISTS raw.coin_prices (
    id                          TEXT        NOT NULL,
    symbol                      TEXT        NOT NULL,
    name                        TEXT        NOT NULL,
    current_price               NUMERIC(24, 8),
    market_cap                  NUMERIC(24, 2),
    market_cap_rank             INTEGER,
    total_volume                NUMERIC(24, 2),
    high_24h                    NUMERIC(24, 8),
    low_24h                     NUMERIC(24, 8),
    price_change_24h            NUMERIC(24, 8),
    price_change_percentage_24h NUMERIC(10, 4),
    circulating_supply          NUMERIC(24, 4),
    total_supply                NUMERIC(24, 4),
    ingested_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, ingested_at)
);

CREATE INDEX IF NOT EXISTS idx_coin_prices_ingested_at
    ON raw.coin_prices (ingested_at DESC);

CREATE INDEX IF NOT EXISTS idx_coin_prices_symbol
    ON raw.coin_prices (symbol);
