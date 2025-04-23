import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO
import yfinance as yf 

# === APP CONFIGURATION ===
st.set_page_config(page_title="FX Strategy Assistant", layout="wide")
st.title("📊 Forex Strategy Assistant")

# === SESSION STATE INIT ===
def initialize_session_state():
    """Initialize all session state variables with default values"""
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
        "candle_pattern": "None",
        "saved_trades": pd.DataFrame()
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# Initialize session state at the start
initialize_session_state()

# === LOGO AND HEADER ===
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://raw.githubusercontent.com/FijabiAdekunle/Forex-Strategy-Assistant-Streamlit-App-/main/Logo%20Images/TopTech_Logo.PNG", width=150)
with col_title:
    st.markdown("### TopTech Digital Intelligence\nUse this app to calculate SL/TP levels using ATR, validate signal alignment, check candlestick confirmation, and manage your trades.")

# === TRADE INPUT SECTION ===
st.header("Trade Input")
col1, col2 = st.columns(2)
with col1:
    st.session_state.pair = st.selectbox(
        "Trading Pair", 
        ["EUR/USD", "GBP/USD", "XAU/USD"], 
        index=["EUR/USD", "GBP/USD", "XAU/USD"].index(st.session_state.pair),
        key="pair_select"
    )
    
    # Replace your entry price widget with this code
new_entry = st.number_input(
    "Entry Price",
    value=float(st.session_state.entry_price),
    step=0.00001,
    format="%.5f",
    key="entry_price_widget"  # Unique key
)

# Update session state only when value changes
if new_entry != st.session_state.entry_price:
    st.session_state.entry_price = new_entry
    st.rerun()  # Force refresh to update calculations
    
    # Dynamic ATR default based on pair
   # Get default ATR based on selected pair
atr_default = 14.50 if st.session_state.pair == "XAU/USD" else 0.00185

st.session_state.atr = st.number_input(
    "ATR Value (in price terms)",
    value=float(st.session_state.get("atr", atr_default)),  # Use dynamic default
    step=0.00001 if st.session_state.pair != "XAU/USD" else 0.01,  # Adjust step based on pair
    format="%.5f" if st.session_state.pair != "XAU/USD" else "%.2f",  # Show 2 decimals for gold
    key="atr_input_unique"
)
with col2:
    st.session_state.sl_multiplier = st.number_input(
        "SL Multiplier", 
        value=st.session_state.sl_multiplier, 
        step=0.1, 
        key="sl_input"
    )
    
    st.session_state.tp_multiplier = st.number_input(
        "TP Multiplier", 
        value=st.session_state.tp_multiplier, 
        step=0.1, 
        key="tp_input"
    )
    
    st.session_state.direction = st.radio(
        "Trade Direction", 
        ["Buy", "Sell"], 
        index=["Buy", "Sell"].index(st.session_state.direction),
        key="direction_radio"
    )

# === INDICATOR INPUT ===
st.header("Indicator Confirmation")
st.session_state.ema_fast = st.number_input(
    "EMA 10",
    value=float(st.session_state.ema_fast),
    step=0.00001,
    format="%.5f",
    key="ema_fast_unique"
)

st.session_state.ema_slow = st.number_input(
    "EMA 50",
    value=float(st.session_state.ema_slow),
    step=0.00001,
    format="%.5f",
    key="ema_slow_unique"
)


st.session_state.rsi = st.number_input(
    "RSI (14)", 
    value=st.session_state.rsi, 
    key="rsi_input"
)

# === CANDLESTICK CONFIRMATION ===
st.header("🕯️ Candlestick Pattern Checklist")
st.session_state.candle_pattern = st.selectbox(
    "Select Pattern", 
    ["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"], 
    index=["None", "Bullish Engulfing", "Bearish Engulfing", "Hammer", "Shooting Star", "Doji"].index(st.session_state.candle_pattern),
    key="candle_select"
)

# === SL/TP CALCULATION ===
if st.session_state.direction == "Buy":
    sl_price = st.session_state.entry_price - (st.session_state.atr * st.session_state.sl_multiplier)
    tp_price = st.session_state.entry_price + (st.session_state.atr * st.session_state.tp_multiplier)
else:
    sl_price = st.session_state.entry_price + (st.session_state.atr * st.session_state.sl_multiplier)
    tp_price = st.session_state.entry_price - (st.session_state.atr * st.session_state.tp_multiplier)

# === SL/TP OUTPUT ===
st.header("📈 SL/TP Levels")
col_sl, col_tp = st.columns(2)
with col_sl:
    st.metric("Stop Loss", f"{sl_price:.5f}", delta=f"{(sl_price - st.session_state.entry_price):.5f}")
with col_tp:
    st.metric("Take Profit", f"{tp_price:.5f}", delta=f"{(tp_price - st.session_state.entry_price):.5f}")

# === INDICATOR ALIGNMENT ===
st.header("🔍 Indicator Alignment Check")
ema_alignment = (
    (st.session_state.ema_fast > st.session_state.ema_slow and st.session_state.direction == "Buy") or 
    (st.session_state.ema_fast < st.session_state.ema_slow and st.session_state.direction == "Sell")
)

rsi_alignment = (
    (st.session_state.rsi > 50 and st.session_state.direction == "Buy") or 
    (st.session_state.rsi < 50 and st.session_state.direction == "Sell")
)

alignment_col1, alignment_col2 = st.columns(2)
with alignment_col1:
    st.write(f"**EMA Alignment:** {'✅ Aligned' if ema_alignment else '❌ Not aligned'}")
with alignment_col2:
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
    
    new_trade = pd.DataFrame(trade_data)
    
    try:
        # Try to load existing trades
        existing_trades = pd.read_csv("saved_trades.csv")
        updated_trades = pd.concat([existing_trades, new_trade], ignore_index=True)
    except FileNotFoundError:
        # If file doesn't exist, create new dataframe
        updated_trades = new_trade
    
    # Save to CSV and update session state
    updated_trades.to_csv("saved_trades.csv", index=False)
    st.session_state.saved_trades = updated_trades
    st.success("Trade saved successfully! ✅")

# === UPLOAD BACKTESTING CSV ===
st.header("📂 Upload Backtesting CSV")
backtest_file = st.file_uploader("Upload your backtest result CSV", type=["csv"])
if backtest_file is not None:
    backtest_df = pd.read_csv(backtest_file)
    st.dataframe(backtest_df.head())
    st.success("Backtesting data loaded successfully! ✅")

# === SAVED TRADES DASHBOARD ===
st.header("📋 Saved Trades Dashboard")

# Load saved trades from file if not in session state
if st.session_state.saved_trades.empty:
    try:
        st.session_state.saved_trades = pd.read_csv("saved_trades.csv")
    except FileNotFoundError:
        st.session_state.saved_trades = pd.DataFrame()

if not st.session_state.saved_trades.empty:
    # Filters
    pair_filter = st.multiselect(
        "Filter by Pair", 
        options=st.session_state.saved_trades["Pair"].unique(),
        default=st.session_state.saved_trades["Pair"].unique()
    )
    
    filtered_trades = st.session_state.saved_trades[
        st.session_state.saved_trades["Pair"].isin(pair_filter)
    ]
    
    st.dataframe(filtered_trades)
    
    # Calculate outcomes
    filtered_trades["Outcome"] = filtered_trades.apply(
        lambda row: "Win" if (
            (row["Direction"] == "Buy" and row["TP"] > row["Entry"]) or 
            (row["Direction"] == "Sell" and row["TP"] < row["Entry"])
        ) else "Loss", 
        axis=1
    )
    
    # Visualization
    fig1 = px.pie(
        filtered_trades, 
        names="Outcome", 
        title="Trade Outcomes Distribution"
    )
    
    fig2 = px.bar(
        filtered_trades,
        x="Pair",
        color="Outcome",
        title="Trades by Currency Pair",
        barmode="group"
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Export options
    st.header("📤 Export Options")
    export_format = st.selectbox(
        "Select export format",
        ["CSV", "Excel", "JSON"]
    )
    
    if export_format == "CSV":
        csv = filtered_trades.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="filtered_trades.csv",
            mime="text/csv"
        )
    elif export_format == "Excel":
        excel = BytesIO()
        filtered_trades.to_excel(excel, index=False)
        st.download_button(
            "Download Excel",
            data=excel.getvalue(),
            file_name="filtered_trades.xlsx",
            mime="application/vnd.ms-excel"
        )
    elif export_format == "JSON":
        json = filtered_trades.to_json(orient="records")
        st.download_button(
            "Download JSON",
            data=json,
            file_name="filtered_trades.json",
            mime="application/json"
        )
else:
    st.info("No saved trades yet. Save your first trade above.")

# === TRADINGVIEW LINK ===
st.header("📊 Chart Analysis")
st.info("For detailed chart analysis, visit TradingView:")
tv_url_map = {
    "EUR/USD": "https://www.tradingview.com/chart/?symbol=FX:EURUSD",
    "GBP/USD": "https://www.tradingview.com/chart/?symbol=FX:GBPUSD",
    "XAU/USD": "https://www.tradingview.com/chart/?symbol=FX:XAUUSD"
}
st.markdown(f"[Open {st.session_state.pair} chart on TradingView ↗️]({tv_url_map[st.session_state.pair]})")

# Live price function 
def get_live_price(pair):
    symbol = {
        "XAU/USD": "GC=F",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X"
    }.get(pair)
    return yf.download(symbol, period="1d", interval="1m").iloc[-1].Close

# Position sizing formula
def calculate_position_size(account_size=10000, risk_pct=1.0):
    price_diff = abs(st.session_state.entry_price - sl_price)
    return (account_size * risk_pct/100) / price_diff

# Using TradingView's calendar
st.components.v1.iframe(
    "https://www.tradingview.com/economic-calendar/",
    height=600,
    scrolling=True
)


# -------------------------------------------------------------------
# NEW SIDEBAR TOOLS 
# -------------------------------------------------------------------
with st.sidebar:
    st.header("🧰 Trading Toolkit")
    
    # ----- LIVE PRICE WIDGET -----
    with st.expander("📊 Live Market Data", expanded=True):
        try:
            current_price = get_live_price(st.session_state.pair)
            st.metric(
                label=f"Live {st.session_state.pair}",
                value=f"{current_price:.5f}",
                delta=f"{(current_price - st.session_state.entry_price):.5f}"
            )
            if st.button("Update Entry Price"):
                st.session_state.entry_price = current_price
                st.rerun()
        except Exception as e:
            st.warning(f"Live data unavailable: {str(e)}")
    
    # ----- RISK CALCULATOR -----
    with st.expander("🧮 Position Sizer", expanded=True):
        account_size = st.number_input(
            "Account Balance ($)", 
            min_value=100, 
            value=10000,
            step=1000
        )
        risk_pct = st.slider(
            "Risk % per Trade", 
            min_value=0.1, 
            max_value=10.0, 
            value=1.0, 
            step=0.1
        )
        
        # Dynamic pip value calculation
        pip_value = 0.0001 if "/" in st.session_state.pair else 0.01
        risk_amount = account_size * (risk_pct / 100)
        price_diff = abs(st.session_state.entry_price - sl_price)
        position_size = risk_amount / price_diff
        
        st.metric(
            "Max Position", 
            f"{position_size:.2f} lots",
            help=f"Risking ${risk_amount:.2f} ({risk_pct}%)"
        )
        
        # Risk visualization
        st.progress(risk_pct/10, text=f"Risk Level: {risk_pct}%")
    
    # ----- ECONOMIC CALENDAR LINK -----
    st.markdown("""
    <div style="margin-top:20px;padding:10px;background:#2E86C1;border-radius:5px">
    <h4 style="color:white;margin:0">📅 Economic Calendar</h4>
    <a href="https://www.tradingview.com/economic-calendar/" target="_blank" style="color:white">View Important Events →</a>
    </div>
    """, unsafe_allow_html=True)

# =====  HELPER FUNCTION  =====
def get_live_price(pair):
    """Fetch live price for selected pair"""
    symbol_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "XAU/USD": "GC=F"
    }
    data = yf.download(symbol_map[pair], period="1d", interval="1m")
    return data["Close"].iloc[-1]