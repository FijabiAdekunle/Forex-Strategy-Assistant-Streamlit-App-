import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO
from PIL import Image

# === APP CONFIGURATION ===
st.set_page_config(page_title="FX Strategy Assistant", layout="wide")
st.title("📊 Forex Strategy Assistant")

# === LOGO AND HEADER ===
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://github.com/FijabiAdekunle/Forex-Strategy-Assistant-Streamlit-App-/blob/main/Logo%20Images/Image.PNG", width=100)
with col_title:
    st.markdown("""
    ### TopTech Digital Intelligence
    Use this app to calculate SL/TP levels using ATR, validate signal alignment, check candlestick confirmation, and manage your trades.
    """)

# === TRADE INPUT SECTION ===
st.header("Trade Input")
col1, col2 = st.columns(2)

with col1:
    pair = st.selectbox("Trading Pair", ["EUR/USD", "GBP/USD", "XAU/USD"])
    entry_price = st.number_input("Entry Price", value=1.0700, step=0.0001, format="%.5f")
    atr = st.number_input("ATR Value (in price terms)", value=0.00185 if pair != "XAU/USD" else 14.5)

with col2:
    sl_multiplier = st.number_input("SL Multiplier", value=1.0, step=0.1)
    tp_multiplier = st.number_input("TP Multiplier", value=2.0, step=0.1)
    direction = st.radio("Trade Direction", ["Buy", "Sell"])

# === INDICATOR INPUT ===
st.header("Indicator Confirmation")
ema_fast = st.number_input("EMA 10", value=1.0720)
ema_slow = st.number_input("EMA 50", value=1.0695)
rsi = st.number_input("RSI (14)", value=56.0)

# === CANDLESTICK CONFIRMATION ===
st.header("🕯️ Candlestick Pattern Checklist")
candle_pattern = st.selectbox("Select Pattern", ["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"])

# === SL/TP CALCULATION ===
if direction == "Buy":
    sl_price = entry_price - atr * sl_multiplier
    tp_price = entry_price + atr * tp_multiplier
else:
    sl_price = entry_price + atr * sl_multiplier
    tp_price = entry_price - atr * tp_multiplier

# === SL/TP OUTPUT ===
st.header("📈 SL/TP Levels")
st.metric("Stop Loss", f"{sl_price:.5f}")
st.metric("Take Profit", f"{tp_price:.5f}")

# === INDICATOR ALIGNMENT ===
st.header("🔍 Indicator Alignment Check")
ema_alignment = (ema_fast > ema_slow and direction == "Buy") or (ema_fast < ema_slow and direction == "Sell")
rsi_alignment = (rsi > 50 and direction == "Buy") or (rsi < 50 and direction == "Sell")

st.write(f"**EMA Alignment:** {'✅ Aligned' if ema_alignment else '❌ Not aligned'}")
st.write(f"**RSI Alignment:** {'✅ Aligned' if rsi_alignment else '❌ Not aligned'}")

if ema_alignment and rsi_alignment and candle_pattern != "None":
    st.success("All indicators + candlestick pattern align ✅")
elif not ema_alignment and not rsi_alignment and candle_pattern == "None":
    st.error("No confirmation from indicators or candlestick ❌")
else:
    st.warning("Partial confirmation. Proceed with caution ⚠️")

# === SAVE TRADE ===
st.header("💾 Save Trade to CSV")
if st.button("Save Trade"):
    trade_data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Pair": [pair],
        "Direction": [direction],
        "Entry": [entry_price],
        "SL": [sl_price],
        "TP": [tp_price],
        "ATR": [atr],
        "SL Multiplier": [sl_multiplier],
        "TP Multiplier": [tp_multiplier],
        "EMA 10": [ema_fast],
        "EMA 50": [ema_slow],
        "RSI": [rsi],
        "Candlestick Pattern": [candle_pattern]
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

    # Outcome Tracking
    saved_trades["Outcome"] = saved_trades.apply(lambda row: "Win" if (row["Direction"] == "Buy" and row["TP"] > row["Entry"]) or (row["Direction"] == "Sell" and row["TP"] < row["Entry"]) else "Loss", axis=1)
    fig = px.pie(saved_trades, names="Outcome", title="Trade Outcomes")
    st.plotly_chart(fig)
except FileNotFoundError:
    st.info("No saved trades yet. Save your first trade above.")

# === EXPORT AS IMAGE OR PDF ===
st.header("🖼️ Export Dashboard Visual")
export_option = st.selectbox("Choose Export Format", ["None", "Export as CSV", "Export as PNG"])
if export_option == "Export as CSV":
    st.download_button("📥 Download CSV", saved_trades.to_csv(index=False), "trades.csv", "text/csv")
elif export_option == "Export as PNG":
    fig = px.bar(saved_trades, x="Pair", y="Entry", color="Outcome", title="Saved Trades by Pair")
    buf = BytesIO()
    fig.write_image(buf, format="png")
    st.download_button("📸 Download PNG", data=buf.getvalue(), file_name="dashboard.png", mime="image/png")

# === PRICE CHART NOTE ===
st.info("⚠️ TradingView charts cannot be embedded directly due to connection policy. Open chart manually in browser.")
if pair == "EUR/USD":
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:EURUSD"
elif pair == "GBP/USD":
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:GBPUSD"
else:
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:XAUUSD"
st.markdown(f"[📈 View {pair} chart on TradingView]({tv_url})")
