# crypto-pulse

> Pipeline ETL horario para las top 50 criptomonedas. CoinGecko API → Postgres → Dashboard Streamlit.

Proyecto de portfolio de **Data Engineering**: ingesta automatizada de precios cripto, modelado relacional con capas `raw`/`marts` y dashboard interactivo.

## Stack
- **Python 3.11+** — extracción y orquestación
- **Prefect 2** — scheduling de flujos
- **PostgreSQL 16** — almacenamiento
- **SQL** (vistas materializadas) — transformaciones
- **Streamlit** — dashboard
- **Docker Compose** — entorno reproducible
- **GitHub Actions** — CI (ruff + pytest)

## Arquitectura

```
CoinGecko API  ──▶  Extractor (Python)  ──▶  Postgres (raw → marts)  ──▶  Streamlit
                          ▲
                          │
                       Prefect (cada 1h)
```

## Quick start

```bash
# 1. Levantar Postgres
docker compose up -d

# 2. Instalar dependencias
pip install -e ".[dev]"

# 3. Copiar variables de entorno
cp .env.example .env

# 4. Ejecutar tests
pytest

# 5. Lanzar el pipeline una vez
python -m crypto_pulse.flows

# 6. Abrir el dashboard
streamlit run dashboard/app.py
```

## Estructura

```
crypto-pulse/
├── src/crypto_pulse/     # código del pipeline
├── sql/                  # esquemas e inicialización de la BD
├── dashboard/            # app Streamlit
├── tests/                # pytest
└── docker-compose.yml    # Postgres
```

## Estado
🚧 En desarrollo activo — ver [issues](../../issues).

## Licencia
MIT
