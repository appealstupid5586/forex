# Skill: Market Analysis

Purpose: Analyze market structure, regime, momentum, volatility, and trend strength. Produces standardized regime-first analysis JSON for downstream skills and decision workflows.

Standard Input: `market_state` (dict containing at least an `ohlcv` table or recent ticks).
Standard Output: JSON with keys: `regime`, `structure`, `momentum`, `volatility`, `strength`, and supporting metadata.

Modules:
- `structure_detector.py` — detect HH-HL, LL-LH, or SIDEWAY structure.
- `volatility_detector.py` — compute ATR state, expansion, and contraction.
- `momentum_detector.py` — evaluate MACD, EMA alignment, and EMA slope.
- `trend_strength.py` — classify strength as weak, normal, or strong.
- `regime_detector.py` — combine structure, momentum, and volatility into a regime.

Constraints: Must not place orders, compute risk sizing, or write journals. Keep logic focused on analysis, evidence generation, and regime classification.
