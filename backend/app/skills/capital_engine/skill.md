# CAPITAL ENGINE

Position sizing engine for approved trades. Computes risk size and position size based on regime, drawdown, and loss streak scaling.

Outputs:
- `risk_size`
- `position_size`
- `regime`
- `risk_multiple`
- `allow_pyramiding`
- `allow_scale_in`
- `allow_wider_trailing_stop`

Strong regime behavior:
- `REGIME_STRONG_BULL`: risk 3R, allow pyramiding, scale in, wider trailing stop
- `REGIME_STRONG_BEAR`: risk 3R, allow scale in
