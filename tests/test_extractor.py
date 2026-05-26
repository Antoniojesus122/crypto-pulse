from unittest.mock import patch, MagicMock
from crypto_pulse.extractor import fetch_top_coins
import pytest
import requests

def test_fetch_top_coins_devuelve_lista_de_monedas():
    #Arrange: preparamos una respuesta falsa de la API
    monedas_falsas = [
        {"id": "bitcoin", "symbol": "btc", "current_price": 70000},
        {"id": "ethereum", "symbol": "eth", "current_price": 3500},
    ]

    respuesta_falsa = MagicMock()
    respuesta_falsa.json.return_value = monedas_falsas
    respuesta_falsa.raise_for_status.return_value = None

    #Act: llamamos a la función con request.get mockeado
    with patch("crypto_pulse.extractor.requests.get", return_value=respuesta_falsa):
        resultado = fetch_top_coins(limit=2)

    #Assert: comprobamos que devolvió lo que la APi "dijo"
    assert resultado == monedas_falsas
    assert len(resultado) == 2
    assert resultado[0]["id"] == "bitcoin"

def test_fetch_top_coins_lanza_excepcion_si_api_falla():
    #Arrange: respuesta falsa que simula un error HTTP 500
    respuesta_falsa = MagicMock()
    respuesta_falsa.raise_for_status.side_effect = requests.HTTPError("500 Server Error")

    #Act + Assert: esperamos que la función propague la excepción
    with patch("crypto_pulse.extractor.requests.get", return_value=respuesta_falsa):
        with pytest.raises(requests.HTTPError):
            fetch_top_coins(limit=5)
