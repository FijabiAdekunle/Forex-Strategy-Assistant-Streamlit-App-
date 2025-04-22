import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO

# === APP CONFIGURATION ===
st.set_page_config(page_title="FX Strategy Assistant", layout="wide")
st.title("📊 Forex Strategy Assistant")

# === SESSION STATE INIT ===
defaults = {
    "pair": "EUR/USD",
    "entry_price": 1.0700,
    "atr": 0.00185,
    "sl_multiplier": 1.0,
    "tp_multiplier": 2.0,
    "direction": "Buy",
    "ema_fast": 1.0720,
    "ema_slow": 1.0695,
    "rsi": 56.0,
    "candle_pattern": "None"
}

# Initialize session state only if it doesn't already exist
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# === LOGO AND HEADER ===
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://raw.githubusercontent.com/FijabiAdekunle/Forex-Strategy-Assistant-Streamlit-App-/main/Logo%20Images/TopTech_Logo.PNG", width=100)
with col_title:
    st.markdown("### TopTech Digital Intelligence\nUse this app to calculate SL/TP levels using ATR, validate signal alignment, check candlestick confirmation, and manage your trades.")

# === TRADE INPUT SECTION ===
st.header("Trade Input")
col1, col2 = st.columns(2)
with col1:
    st.session_state.pair = st.selectbox("Trading Pair", ["EUR/USD", "GBP/USD", "XAU/USD"], index=["EUR/USD", "GBP/USD", "XAU/USD"].index(st.session_state.pair), key="pair")
    st.session_state.entry_price = st.number_input("Entry Price", value=st.session_state.entry_price, step=0.0001, format="%.5f", key="entry_price")
    st.session_state.atr = st.number_input("ATR Value (in price terms)", value=st.session_state.atr if st.session_state.pair != "XAU/USD" else 14.5, key="atr")
with col2:
    st.session_state.sl_multiplier = st.number_input("SL Multiplier", value=st.session_state.sl_multiplier, step=0.1, key="sl_multiplier")
    st.session_state.tp_multiplier = st.number_input("TP Multiplier", value=st.session_state.tp_multiplier, step=0.1, key="tp_multiplier")
    st.session_state.direction = st.radio("Trade Direction", ["Buy", "Sell"], index=["Buy", "Sell"].index(st.session_state.direction), key="direction")

# === INDICATOR INPUT ===
st.header("Indicator Confirmation")
st.session_state.ema_fast = st.number_input("EMA 10", value=st.session_state.ema_fast, key="ema_fast")
st.session_state.ema_slow = st.number_input("EMA 50", value=st.session_state.ema_slow, key="ema_slow")
st.session_state.rsi = st.number_input("RSI (14)", value=st.session_state.rsi, key="rsi")

# === CANDLESTICK CONFIRMATION ===
st.header("🕯️ Candlestick Pattern Checklist")
st.session_state.candle_pattern = st.selectbox("Select Pattern", ["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"], index=["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"].index(st.session_state.candle_pattern), key="candle_pattern")

# === SL/TP CALCULATION ===
if st.session_state.direction == "Buy":
    sl_price = st.session_state.entry_price - st.session_state.atr * st.session_state.sl_multiplier
    tp_price = st.session_state.entry_price + st.session_state.atr * st.session_state.tp_multiplier
else:
    sl_price = st.session_state.entry_price + st.session_state.atr * st.session_state.sl_multiplier
    tp_price = st.session_state.entry_price - st.session_state.atr * st.session_state.tp_multiplier

# === SL/TP OUTPUT ===
st.header("📈 SL/TP Levels")
st.metric("Stop Loss", f"{sl_price:.5f}")
st.metric("Take Profit", f"{tp_price:.5f}")

# === INDICATOR ALIGNMENT ===
st.header("🔍 Indicator Alignment Check")
ema_alignment = (st.session_state.ema_fast > st.session_state.ema_slow and st.session_state.direction == "Buy") or (st.session_state.ema_fast < st.session_state.ema_slow and st.session_state.direction == "Sell")
rsi_alignment = (st.session_state.rsi > 50 and st.session_state.direction == "Buy") or (st.session_state.rsi < 50 and st.session_state.direction == "Sell")

st.write(f"**EMA Alignment:** {'✅ Aligned' if ema_alignment else '❌ Not aligned'}")
st.write(f"**RSI Alignment:** {'✅ Aligned' if rsi_alignment else '❌ Not aligned'}")

if ema_alignment and rsi_alignment and st.session_state.candle_pattern != "None":
    st.success("All indicators + candlestick pattern align ✅")
elif not ema_alignment and not rsi_alignment and st.session_state.candle_pattern == "None":
    st.error("No confirmation from indicators or candlestick ❌")
else:
    st.warning("Partial confirmation. Proceed with caution ⚠️")

# === SAVE TRADE ===
st.header("💾 Save Trade to CSV")
if st.button("Save Trade"):
    trade_data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Pair": [st.session_state.pair],
        "Direction": [st.session_state.direction],
        "Entry": [st.session_state.entry_price],
        "SL": [sl_price],
        "TP": [tp_price],
        "ATR": [st.session_state.atr],
        "SL Multiplier": [st.session_state.sl_multiplier],
        "TP Multiplier": [st.session_state.tp_multiplier],
        "EMA 10": [st.session_state.ema_fast],
        "EMA 50": [st.session_state.ema_slow],
        "RSI": [st.session_state.rsi],
        "Candlestick Pattern": [st.session_state.candle_pattern]
    }
    df = pd.DataFrame(trade_data)
    try:
        existing = pd.read_csv("saved_trades.csv")
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv("saved_trades.csv", index=False)
    st.success("Trade saved to saved_trades.csv ✅")

# === UPLOAD BACKTESTING CSV ===
st.header("📂 Upload Backtesting CSV")
backtest_file = st.file_uploader("Upload your backtest result CSV", type="csv")
if backtest_file:
    backtest_df = pd.read_csv(backtest_file)
    st.dataframe(backtest_df)
    st.success("Backtesting data loaded ✅")

# === SAVED TRADES DASHBOARD ===
st.header("📋 Saved Trades Dashboard")
try:
    saved_trades = pd.read_csv("saved_trades.csv")
    filters = st.multiselect("Filter by Pair", saved_trades["Pair"].unique())
    if filters:
        saved_trades = saved_trades[saved_trades["Pair"].isin(filters)]
    st.dataframe(saved_trades)

    saved_trades["Outcome"] = saved_trades.apply(
        lambda row: "Win" if (row["Direction"] == "Buy" and row["TP"] > row["Entry"]) or (row["Direction"] == "Sell" and row["TP"] < row["Entry"]) else "Loss", axis=1)
    fig = px.pie(saved_trades, names="Outcome", title="Trade Outcomes")
    st.plotly_chart(fig)
except FileNotFoundError:
    st.info("No saved trades yet. Save your first trade above.")
