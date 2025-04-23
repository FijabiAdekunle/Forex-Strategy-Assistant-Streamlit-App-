# ===== [ADD TO IMPORTS SECTION] =====
import yfinance as yf  # Add this at the top with other imports

# ===== [ADD THIS AFTER TRADINGVIEW LINK SECTION] =====
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

# ===== [ADD THIS HELPER FUNCTION] =====
def get_live_price(pair):
    """Fetch live price for selected pair"""
    symbol_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "XAU/USD": "GC=F"
    }
    data = yf.download(symbol_map[pair], period="1d", interval="1m")
    return data["Close"].iloc[-1]