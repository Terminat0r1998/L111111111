"""
Premium ROC Acceleration Burst Strategy Engine
"""

import numpy as np
from typing import List, Optional

class PremiumROCAcceleration:
    def __init__(self, roc_period: int = 5, accel_threshold: float = 1.8):
        self.roc_period = roc_period
        self.accel_threshold = accel_threshold
        self.premium_history: List[float] = []

    def update(self, premium: float) -> Optional[dict]:
        self.premium_history.append(premium)
        if len(self.premium_history) > 50:
            self.premium_history.pop(0)

        if len(self.premium_history) < self.roc_period + 2:
            return None

        prices = np.array(self.premium_history)
        roc = (prices[-1] - prices[-self.roc_period]) / prices[-self.roc_period] * 100
        prev_roc = (prices[-2] - prices[-self.roc_period-1]) / prices[-self.roc_period-1] * 100
        acceleration = roc - prev_roc

        if roc > 3.0 and acceleration > self.accel_threshold:
            entry = premium
            sl = round(entry * 0.82, 2)
            target = round(entry * 1.25, 2)
            return {
                "type": "BUY_CE",
                "entry": entry,
                "stop_loss": sl,
                "target": target,
                "roc": round(roc, 2),
                "acceleration": round(acceleration, 2),
                "confidence": min(99, int(70 + acceleration * 8)),
            }
        return None