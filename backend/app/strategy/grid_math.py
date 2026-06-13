from __future__ import annotations

from app.core.models import GridState


def calculate_grid(symbol: str, base_price: float, current_price: float, step_size: float, x_level: int, tick_size: float) -> GridState:
    upper_level = base_price + step_size * x_level
    lower_level = base_price - step_size * x_level
    return GridState(
        symbol=symbol,
        base_price=base_price,
        current_price=current_price,
        step_size=step_size,
        x_level=x_level,
        tick_size=tick_size,
        current_step=0,
        step_price=base_price,
        upper_level=upper_level,
        lower_level=lower_level,
        step_distance=step_size,
    )
