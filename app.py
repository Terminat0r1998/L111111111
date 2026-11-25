"""
Nifty Premium ROC Acceleration Dashboard
With Telegram alerts
"""

import streamlit as st
import time
import requests
from datetime import datetime
from nse_data import NSEOptions
from strategy_engine import PremiumROCAcceleration

st.set_page_config(
    page_title="Nifty Signals — ROC Acceleration",
    page_icon="📈",
    layout="wide",
)

# Telegram helper
def send_telegram(message: str):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        st.warning(f"Telegram send failed: {e}")

st.markdown("""
<style>
    .stApp { background: #0e1117; color: #fafafa; }
    .signal-card {
        background: #1e1e1e; border: 1px solid #333; border-radius: 12px;
        border-left: 5px solid #00c853; padding: 16px; margin: 10px 0; color: #fafafa;
    }
    .buy-badge { background: #00c853; color: #000; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .active-badge { background: #1b5e20; color: #a5d6a7; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
    .conf-badge { background: #f9a825; color: #000; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
    .level-box { background: #2a2a2a; border-radius: 8px; padding: 10px; text-align: center; color: #fafafa; }
    h1, h2, h3, .stMarkdown, p, span, div { color: #fafafa !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("### Live Signals · 24 Strategy Workers · Signal Matrix")
st.caption("Premium ROC Acceleration Burst — Telegram alerts enabled")

if "nse" not in st.session_state:
    st.session_state.nse = NSEOptions()
    st.session_state.strategy = PremiumROCAcceleration()
    st.session_state.signal = None
    st.session_state.entry = None
    st.session_state.history = []
    st.session_state.alerted = False

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

                st.success(f"Spot ₹{data['spot']:.2f} · {data['instrument']} · LTP ₹{ltp:.2f}")

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
                    # Send Telegram alert (only once per signal)
                    if not st.session_state.alerted:
                        msg = (
                            f"🚀 <b>NIFTY ROC BURST</b>\n\n"
                            f"<b>{data['instrument']}</b>\n"
                            f"Entry: ₹{result['entry']:.2f}\n"
                            f"SL: ₹{result['stop_loss']:.2f}\n"
                            f"Target: ₹{result['target']:.2f}\n"
                            f"Confidence: {result['confidence']}%\n"
                            f"Spot: ₹{data['spot']:.2f}\n"
                            f"Time: {datetime.now().strftime('%H:%M:%S')}"
                        )
                        send_telegram(msg)
                        st.session_state.alerted = True
                        st.toast("Telegram alert sent")

                elif st.session_state.signal:
                    st.session_state.signal["ltp"] = ltp
                    st.session_state.signal["time"] = datetime.now().strftime("%I:%M:%S %p").lower()

                st.session_state.history.append(ltp)
                if len(st.session_state.history) > 30:
                    st.session_state.history.pop(0)
            else:
                st.warning("No data from NSE")
        except Exception as e:
            st.error(f"Error: {e}")

# Display card (same as before)
if st.session_state.signal:
    sig = st.session_state.signal
    entry = st.session_state.entry or sig["entry"]
    change = ((sig["ltp"] - entry) / entry) * 100 if entry else 0

    st.markdown(f"""
    <div class="signal-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div><span class="buy-badge">↗ BUY_CE</span>
            <strong style="font-size:18px; margin-left:10px; color:#fff;">{sig['instrument']}</strong></div>
            <div><span class="active-badge">● LIVE</span> <span class="conf-badge">{sig['confidence']}%</span></div>
        </div>
        <div style="margin:8px 0; color:#ccc;">{sig['expiry']}</div>
        <div style="font-weight:bold; color:#fff; margin:8px 0;">
            ✦ S16: Premium ROC Acceleration Burst
            <span style="float:right; background:#333; padding:4px 10px; border-radius:6px;">⏱ {sig['time']}</span>
        </div>
        <div style="display:flex; gap:12px; margin:12px 0;">
            <div class="level-box" style="flex:1;"><div style="color:#aaa;">ENTRY</div><div style="font-size:18px; font-weight:bold;">₹{sig['entry']:.2f}</div></div>
            <div class="level-box" style="flex:1;"><div style="color:#aaa;">STOP LOSS</div><div style="font-size:18px; font-weight:bold; color:#ff5252;">₹{sig['sl']:.2f}</div></div>
            <div class="level-box" style="flex:1;"><div style="color:#aaa;">TARGET 1</div><div style="font-size:18px; font-weight:bold; color:#69f0ae;">₹{sig['target']:.2f}</div></div>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="background:#1565c0; color:#fff; padding:6px 12px; border-radius:16px;">● 6 Confirmations</span>
            <span style="background:#1b5e20; color:#a5d6a7; padding:4px 10px; border-radius:6px;">LTP ₹{sig['ltp']:.2f} ({change:+.1f}%)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.history) > 2:
        st.line_chart(st.session_state.history, height=120)
else:
    st.info("Waiting for ROC Acceleration burst... Telegram alert will be sent when it triggers.")

st.caption("Data from NSE. Educational use only. Not financial advice.")

if auto:
    time.sleep(interval)
    st.rerun()