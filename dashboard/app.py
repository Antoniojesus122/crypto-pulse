import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from sqlalchemy import text

from crypto_pulse.loader import engine

st.set_page_config(
    page_title="Crypto Pulse",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Crypto Pulse")
st.caption("Pipeline ETL horario para las top 50 criptomonedas")

@st.cache_data(ttl=60)
def query(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return pd.DataFrame(result.fetchall(), columns=list(result.keys()))
    
st.header("Resumen de mercado")

resumen = query("""
    SELECT
        COUNT(*) AS n_coins,
        SUM(market_cap) AS total_market_cap,
        MAX(ingested_at) AS last_update,
        SUM(CASE WHEN id = 'bitcoin' THEN market_cap ELSE 0 END)
            / NULLIF(SUM(market_cap), 0) * 100 AS btc_dominance
    FROM marts.coins_latest
""")

fila = resumen.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monedas tracked", f"{int(fila['n_coins'])}")
col2.metric("Market cap total", f"${float(fila['total_market_cap']) / 1e9:.1f}B")
col3.metric("Dominancia BTC", f"{float(fila['btc_dominance']):.1f}%")
col4.metric("Última actualización", fila["last_update"].strftime("%H:%M:%S"))

st.header("Top movers 24h")

movers = query("""
    SELECT direction, symbol, name, current_price, price_change_percentage_24h
    FROM marts.top_movers_24h
""")

col_gainers, col_losers = st.columns(2)

with col_gainers:
    st.subheader("📈 Ganadoras")
    gainers = movers[movers["direction"] == "gainer"].drop(columns=["direction"])
    st.dataframe(gainers, hide_index=True, use_container_width=True)

with col_losers:
    st.subheader("📉 Perdedoras")
    losers = movers[movers["direction"] == "loser"].drop(columns=["direction"])
    st.dataframe(losers, hide_index=True, use_container_width=True)

st.header("Detalle de moneda")

#Selector de moneda (las top 50)
coins = query("""
    SELECT id, symbol, name
    FROM marts.coins_latest
    ORDER BY market_cap_rank
""")

opciones = {f"{row['name']} ({row['symbol'].upper()})": row['id'] for _, row in coins.iterrows()}
seleccionada = st.selectbox("Elige una moneda", options=list(opciones.keys()))
coin_id = opciones[seleccionada]

#OHLC diario de la moneda
ohlc = query(f"""
    SELECT day, open, high, low, close, ticks
    FROM marts.daily_ohlc
    WHERE id = '{coin_id}'
    ORDER BY day
""")

if ohlc.empty:
    st.info("Todavía no hay datos diarios suficientes para esta moneda.")
else:
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=ohlc["day"],
                open=ohlc["open"],
                high=ohlc["high"],
                low=ohlc["low"],
                close=ohlc["close"],
                name=seleccionada,
            )
        ]
    )
    fig.update_layout(
        title=f"OHLC diario - {seleccionada}",
        xaxis_title="Día",
        yaxis_title="Precio (USD)",
        xaxis_rangeslider_visible=False,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Total de días con datos: {len(ohlc)} · Total ticks: {int(ohlc['ticks'].sum())}")

st.header("Volatilidad (7 días)")

volatilidad = query("""
    SELECT
        symbol,
        ROUND(avg_price_7d::numeric, 4) AS precio_medio,
        ROUND(volatility_pct_7d::numeric, 2) AS volatilidad_pct,
        ticks_7d AS ticks
    FROM marts.volatility_7d
    WHERE volatility_pct_7d IS NOT NULL
    ORDER BY volatility_pct_7d DESC
    LIMIT 20
""")
st.dataframe(volatilidad, hide_index=True, use_container_width=True)
st.caption("Coeficiente de variación del precio (desviación estándar / media * 100). Mayor % = más volátil.")