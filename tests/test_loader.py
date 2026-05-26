import pytest
from sqlalchemy import text

from crypto_pulse.loader import engine ,load_coins

def test_load_coins_lista_vacia_devuelve_cero():
    resultado = load_coins([])
    assert resultado == 0

@pytest.fixture
def tabla_limpia():
    """Vacía la tabla raw.coin_prices antes y después del test."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE raw.coin_prices"))
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE raw.coin_prices"))

def test_load_coins_inserta_en_postgres(tabla_limpia):
    #Arrange: 2 monedas falsas con los campos mínimos
    monedas = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 70000},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3500},
    ]

    #Act: cargar
    insertadas = load_coins(monedas)

    #Assert 1: la función reporta 2 insertadas
    assert insertadas == 2

    #Assert 2: la DB tiene esas 2 filas
    with engine.begin() as conn:
        resultado = conn.execute(
            text("SELECT id, symbol, current_price FROM raw.coin_prices ORDER BY id")
            ).all()

    assert len(resultado) == 2
    assert resultado[0].id == "bitcoin"
    assert resultado[0].current_price == 70000
    assert resultado[1].id == "ethereum"