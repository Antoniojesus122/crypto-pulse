from typing import Any

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from crypto_pulse.config import settings

engine: Engine = create_engine(settings.database_url, pool_pre_ping=True)

COLUMNAS = [
    "id",
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "market_cap_rank",
    "total_volume",
    "high_24h",
    "low_24h",
    "price_change_24h",
    "price_change_percentage_24h",
    "circulating_supply",
    "total_supply",
]

def load_coins(coins: list[dict[str, Any]]) -> int:
    if not coins:
        logger.warning("Lista de monedas vacía, nada que insertar")
        return 0
    
    columnas_sql = ", ".join(COLUMNAS)
    placeholders = ", ".join(f":{c}" for c in COLUMNAS)
    sql = text(
        f"INSERT INTO raw.coin_prices ({columnas_sql})"
        f"VALUES ({placeholders})"
    )

    filas = [{c: coin.get(c) for c in COLUMNAS} for coin in coins]

    with engine.begin() as conn:
        conn.execute(sql, filas)
    
    logger.info(f"Insertadas {len(filas)} filas en raw.coin_prices")
    return len(filas)

if __name__ == "__main__":
    from crypto_pulse.extractor import fetch_top_coins

    monedas = fetch_top_coins(limit=10)
    insertadas = load_coins(monedas)
    logger.info(f"Pipeline completo: {insertadas} monedas cargadas en Postgress")