from __future__ import annotations


class HedgeEngine:
    def __init__(self, base_lot, max_exposure_lots):
        self.base_lot = base_lot
        self.max_exposure_lots = max_exposure_lots
