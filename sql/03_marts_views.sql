-- marts.coins_latest - último snapshot disponible de cada moneda
CREATE OR REPLACE VIEW marts.coins_latest AS
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY ingested_at DESC) AS rn
    FROM raw.coin_prices
)
SELECT 
    id,
    symbol,
    name,
    current_price,
    market_cap,
    market_cap_rank,
    total_volume,
    price_change_percentage_24h,
    ingested_at
FROM ranked
WHERE rn = 1;

-- marts.top_movers_24h - 10 mayores subidas + 10 mayores bajadas en 24h
CREATE OR REPLACE VIEW marts.top_movers_24h AS
(
    SELECT
        'gainer' AS direction,
        id,
        symbol,
        name,
        current_price,
        price_change_percentage_24h
    FROM marts.coins_latest
    WHERE price_change_percentage_24h IS NOT NULL
    ORDER BY price_change_percentage_24h DESC
    LIMIT 10
)
UNION ALL
(
    SELECT
        'loser' AS direction,
        id,
        symbol,
        name,
        current_price,
        price_change_percentage_24h
    FROM marts.coins_latest
    WHERE price_change_percentage_24h IS NOT NULL
    ORDER BY price_change_percentage_24h ASC
    LIMIT 10
);

-- marts.daily_ohlc - Open/High/Low/Clone diario por moneda
CREATE MATERIALIZED VIEW IF NOT EXISTS marts.daily_ohlc AS
WITH ranked AS (
    SELECT
        id,
        symbol,
        DATE_TRUNC('day', ingested_at)::date AS day,
        current_price,
        ROW_NUMBER() OVER (
            PARTITION BY id, DATE_TRUNC('day', ingested_at)
            ORDER BY ingested_at ASC
        ) AS rn_asc,
        ROW_NUMBER() OVER (
            PARTITION BY id, DATE_TRUNC('day', ingested_at)
            ORDER BY ingested_at DESC
        ) AS rn_desc
    FROM raw.coin_prices
    WHERE current_price IS NOT NULL
)
SELECT
    id,
    symbol,
    day,
    MAX(current_price) FILTER (WHERE rn_asc = 1) AS open,
    MAX(current_price) AS high,
    MIN(current_price) AS low,
    MAX(current_price) FILTER (WHERE rn_desc = 1) AS close,
    COUNT(*) AS ticks
FROM ranked
GROUP BY id, symbol, day;

CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_ohlc_pk
    ON marts.daily_ohlc (id, day);

-- marts.volatility_7d - coeficiente de variación de precio (%) últimos 7 días
CREATE MATERIALIZED VIEW IF NOT EXISTS marts.volatility_7d AS
SELECT
    id,
    symbol,
    AVG(current_price) AS avg_price_7d,
    STDDEV(current_price) AS stddev_price_7d,
    STDDEV(current_price) / NULLIF(AVG(current_price), 0) * 100 AS volatility_pct_7d,
    COUNT(*) AS ticks_7d
FROm raw.coin_prices
WHERE ingested_at >= NOW() - INTERVAL '7 days'
    AND current_price IS NOT NULL
GROUP BY id, symbol;

CREATE UNIQUE INDEX IF NOT EXISTS idx_volatility_7d_pk
    ON marts.volatility_7d (id);