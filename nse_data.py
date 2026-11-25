"""
Live NSE Nifty Options Data Fetcher
"""

from curl_cffi import requests
from datetime import datetime

class NSEOptions:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/option-chain",
        }
        self._init_session()

    def _init_session(self):
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, impersonate="chrome", timeout=10)
        except Exception:
            pass

    def get_option_chain(self, symbol="NIFTY", expiry=None):
        if not expiry:
            info = self.session.get(
                "https://www.nseindia.com/api/option-chain-contract-info",
                params={"symbol": symbol},
                headers=self.headers,
                impersonate="chrome",
                timeout=15,
            )
            expiries = info.json().get("expiryDates", [])
            expiry = expiries[0] if expiries else None

        if not expiry:
            return None

        url = "https://www.nseindia.com/api/option-chain-v3"
        params = {"type": "Indices", "symbol": symbol, "expiry": expiry}
        r = self.session.get(url, params=params, headers=self.headers, impersonate="chrome", timeout=20)
        data = r.json()
        records = data.get("records", {})

        result = {
            "spot": records.get("underlyingValue"),
            "expiry": expiry,
            "timestamp": records.get("timestamp"),
            "strikes": [],
        }

        for row in records.get("data", []):
            strike = row.get("strikePrice")
            ce = row.get("CE") or {}
            pe = row.get("PE") or {}
            result["strikes"].append({
                "strike": strike,
                "ce_ltp": ce.get("lastPrice"),
                "ce_oi": ce.get("openInterest"),
                "ce_volume": ce.get("totalTradedVolume"),
                "ce_iv": ce.get("impliedVolatility"),
                "ce_change": ce.get("change"),
                "pe_ltp": pe.get("lastPrice"),
                "pe_oi": pe.get("openInterest"),
                "pe_volume": pe.get("totalTradedVolume"),
                "pe_iv": pe.get("impliedVolatility"),
            })

        return result

    def get_atm_call(self, symbol="NIFTY"):
        chain = self.get_option_chain(symbol)
        if not chain or not chain["spot"]:
            return None

        spot = chain["spot"]
        best = None
        best_diff = float("inf")
        for s in chain["strikes"]:
            diff = abs(s["strike"] - spot)
            if diff < best_diff and s["ce_ltp"]:
                best_diff = diff
                best = s

        if not best:
            return None

        return {
            "instrument": f"{symbol} {int(best['strike'])} CE",
            "strike": best["strike"],
            "ltp": best["ce_ltp"],
            "oi": best["ce_oi"],
            "volume": best["ce_volume"],
            "iv": best["ce_iv"],
            "spot": spot,
            "expiry": chain["expiry"],
            "timestamp": chain["timestamp"],
        }