import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FX Strategy Assistant", layout="centered")
st.title("📊 Forex Strategy Assistant")
st.markdown("""
Use this app to calculate SL/TP levels using ATR, validate signal alignment, check candlestick confirmation, and manage your trades.
""")

# Input Section
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

# Indicator Alignment Input
st.header("Indicator Confirmation")
ema_fast = st.number_input("EMA 10", value=1.0720)
ema_slow = st.number_input("EMA 50", value=1.0695)
rsi = st.number_input("RSI (14)", value=56)

# Candlestick Pattern Checklist
st.header("🕯️ Candlestick Pattern Checklist")
candle_pattern = st.selectbox("Select Pattern", ["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"])

# Calculate SL and TP
if direction == "Buy":
    sl_price = entry_price - atr * sl_multiplier
    tp_price = entry_price + atr * tp_multiplier
else:
    sl_price = entry_price + atr * sl_multiplier
    tp_price = entry_price - atr * tp_multiplier

# Results Section
st.header("📈 SL/TP Levels")
st.write(f"**Stop Loss:** {sl_price:.5f}")
st.write(f"**Take Profit:** {tp_price:.5f}")

# Signal Alignment Section
st.header("🔍 Indicator Alignment Check")
ema_alignment = (ema_fast > ema_slow and direction == "Buy") or (ema_fast < ema_slow and direction == "Sell")
rsi_alignment = (rsi > 50 and direction == "Buy") or (rsi < 50 and direction == "Sell")

st.write(f"**EMA Alignment:** {'✅ Aligned' if ema_alignment else '❌ Not aligned'}")
st.write(f"**RSI Alignment:** {'✅ Aligned' if rsi_alignment else '❌ Not aligned'}")

# Summary
if ema_alignment and rsi_alignment and candle_pattern != "None":
    st.success("All indicators + candlestick pattern align ✅")
elif not ema_alignment and not rsi_alignment and candle_pattern == "None":
    st.error("No confirmation from indicators or candlestick ❌")
else:
    st.warning("Partial confirmation. Proceed with caution ⚠️")

# Save Trade Section
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

# Backtesting Section
st.header("📂 Upload Backtesting CSV")
backtest_file = st.file_uploader("Upload your backtest result CSV", type="csv")
if backtest_file:
    backtest_df = pd.read_csv(backtest_file)
    st.dataframe(backtest_df)
    st.success("Backtesting data loaded ✅")

# Saved Trades Dashboard
st.header("📋 Saved Trades Dashboard")
try:
    saved_trades = pd.read_csv("saved_trades.csv")
    st.dataframe(saved_trades)
except FileNotFoundError:
    st.info("No saved trades yet. Save your first trade above.")

# Price Chart Preview
st.header("📉 Price Chart Preview")
if pair == "EUR/USD":
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:EURUSD"
elif pair == "GBP/USD":
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:GBPUSD"
else:
    tv_url = "https://www.tradingview.com/chart/?symbol=FX:XAUUSD"

st.components.v1.iframe(tv_url, height=450, scrolling=True)
