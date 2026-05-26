import requests
from typing import Any
from crypto_pulse.config import settings
from loguru import logger

def fetch_top_coins(
    limit: int = settings.coingecko_top_n, 
    vs_currency: str = settings.coingecko_vs_currency,
    ) -> list[dict[str, Any]]:

    url = f"{settings.coingecko_base_url}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
    }

    logger.info(f"Solicitando top {limit} monedas a CoinGecko ({vs_currency})")
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    logger.info(f"Recibidas {len(data)} monedas")
    return data

if __name__ == "__main__":
    coins = fetch_top_coins(limit=5)
    print(f"recibidas {len(coins)} monedas")
    for coin in coins:
        print(f" - {coin['symbol'].upper()}: ${coin['current_price']}")