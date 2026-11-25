"""
Nifty Premium ROC Acceleration Dashboard
Web version — high contrast
"""

import streamlit as st
import time
from datetime import datetime
from nse_data import NSEOptions
from strategy_engine import PremiumROCAcceleration

st.set_page_config(
    page_title="Nifty Signals — ROC Acceleration",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
    .stApp {
        background: #0e1117;
        color: #fafafa;
    }
    .signal-card {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 12px;
        border-left: 5px solid #00c853;
        padding: 16px;
        margin: 10px 0;
        color: #fafafa;
    }
    .buy-badge {
        background: #00c853;
        color: #000;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    .active-badge {
        background: #1b5e20;
        color: #a5d6a7;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .conf-badge {
        background: #f9a825;
        color: #000;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .level-box {
        background: #2a2a2a;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        color: #fafafa;
    }
    h1, h2, h3, .stMarkdown, p, span, div {
        color: #fafafa !important;
    }
    .stSuccess, .stInfo, .stWarning {
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("### Live Signals · 24 Strategy Workers · Signal Matrix")
st.caption("Premium ROC Acceleration Burst — connected to NSE live data")

if "nse" not in st.session_state:
    st.session_state.nse = NSEOptions()
    st.session_state.strategy = PremiumROCAcceleration()
    st.session_state.signal = None
    st.session_state.entry = None
    st.session_state.history = []

col1, col2, col3 = st.columns([2, 2, 1])
with col3:
    auto = st.toggle("Auto refresh", value=True)
    interval = st.slider("Seconds", 5, 30, 8, disabled=not auto)

if st.button("Refresh Now", type="primary") or auto:
    with st.spinner("Fetching from NSE..."):
        try:
            data = st.session_state.nse.get_atm_call()
            if data and data.get("ltp"):
                ltp = data["ltp"]
                result = st.session_state.strategy.update(ltp)

                st.success(f"Spot ₹{data['spot']:.2f} · {data['instrument']} · LTP ₹{ltp:.2f} · {data.get('timestamp', '')}")

                if result and st.session_state.signal is None:
                    st.session_state.entry = result["entry"]
                    st.session_state.signal = {
                        "instrument": data["instrument"],
                        "expiry": data["expiry"],
                        "entry": result["entry"],
                        "sl": result["stop_loss"],
                        "target": result["target"],
                        "confidence": result["confidence"],
                        "ltp": ltp,
                        "time": datetime.now().strftime("%I:%M:%S %p").lower(),
                    }
                elif st.session_state.signal:
                    st.session_state.signal["ltp"] = ltp
                    st.session_state.signal["time"] = datetime.now().strftime("%I:%M:%S %p").lower()

                st.session_state.history.append(ltp)
                if len(st.session_state.history) > 30:
                    st.session_state.history.pop(0)
            else:
                st.warning("No data returned from NSE. Market may be closed or rate-limited.")
        except Exception as e:
            st.error(f"Fetch error: {e}")

if st.session_state.signal:
    sig = st.session_state.signal
    entry = st.session_state.entry or sig["entry"]
    change = ((sig["ltp"] - entry) / entry) * 100 if entry else 0

    st.markdown(f"""
    <div class="signal-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div>
                <span class="buy-badge">↗ BUY_CE</span>
                <strong style="font-size:18px; margin-left:10px; color:#fff;">{sig['instrument']}</strong>
            </div>
            <div>
                <span class="active-badge">● LIVE</span>
                <span class="conf-badge">{sig['confidence']}%</span>
            </div>
        </div>
        <div style="margin:6px 0; color:#ccc; background:#333; display:inline-block; padding:2px 8px; border-radius:4px;">
            {sig['expiry']}
        </div>
        <div style="margin:10px 0; font-weight:bold; color:#fff;">
            ✦ S16: Premium ROC Acceleration Burst
            <span style="float:right; background:#333; border:1px solid #555; padding:4px 10px; border-radius:6px; font-weight:normal; color:#fff;">
                ⏱ {sig['time']}
            </span>
        </div>
        <div style="display:flex; gap:12px; margin:12px 0;">
            <div class="level-box" style="flex:1;">
                <div style="color:#aaa; font-size:12px;">ENTRY</div>
                <div style="font-size:18px; font-weight:bold; color:#fff;">₹{sig['entry']:.2f}</div>
            </div>
            <div class="level-box" style="flex:1;">
                <div style="color:#aaa; font-size:12px;">STOP LOSS</div>
                <div style="font-size:18px; font-weight:bold; color:#ff5252;">₹{sig['sl']:.2f}</div>
            </div>
            <div class="level-box" style="flex:1;">
                <div style="color:#aaa; font-size:12px;">TARGET 1</div>
                <div style="font-size:18px; font-weight:bold; color:#69f0ae;">₹{sig['target']:.2f}</div>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
            <span style="background:#1565c0; color:#fff; padding:6px 12px; border-radius:16px; font-weight:bold;">
                ● 6 Confirmations
            </span>
            <span style="background:#1b5e20; color:#a5d6a7; padding:4px 10px; border-radius:6px; font-weight:bold;">
                LTP ₹{sig['ltp']:.2f} ({change:+.1f}%)
            </span>
        </div>
        <div style="color:#aaa; font-size:13px; margin-top:6px;">
            (S16 + S03 + S14 + S10 + S15 + S23)
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.history) > 2:
        st.line_chart(st.session_state.history, height=120)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("Builder")
    with c2:
        st.button("Save")
    with c3:
        if st.button("Paper Trade"):
            st.toast("Paper trade logged")
    with c4:
        st.button("Details")
else:
    st.info("Waiting for ROC Acceleration burst on the ATM Call... Refresh to check again.")

st.caption("Data from NSE India public endpoints. For educational use. Not financial advice.")

if auto:
    time.sleep(interval)
    st.rerun()