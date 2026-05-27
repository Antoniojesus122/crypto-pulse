from prefect import flow, task
from sqlalchemy import text

from crypto_pulse.extractor import fetch_top_coins
from crypto_pulse.loader import engine, load_coins

@task(retries=3, retry_delay_seconds=30, log_prints=True)
def extraer_monedas(limit: int = 50) -> list[dict]:
    return fetch_top_coins(limit=limit)

@task(log_prints=True)
def cargar_monedas(monedas: list[dict]) -> int:
    return load_coins(monedas)

@task(log_prints=True)
def refrescar_marts() -> None:
    vistas_materializadas = ["marts.daily_ohlc", "marts.volatility_7d"]
    with engine.begin() as conn:
        for vista in vistas_materializadas:
            conn.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {vista}"))
            print(f"Refrescada vista materializada {vista}")

@flow(name="crypto-pulse.hourly", log_prints=True)
def crypto_pulse_pipeline(limit: int = 50) -> int:
    monedas = extraer_monedas(limit=limit)
    insertadas = cargar_monedas(monedas)
    refrescar_marts()
    print(f"Pipeline completado: {insertadas} monedas insertadas")
    return insertadas

if __name__ == "__main__":
    crypto_pulse_pipeline.serve(
        name="crypto-pulse-hourly-deployment",
        interval=3600,
        tags=["crypto", "etl"],
    )
