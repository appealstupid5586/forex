from __future__ import annotations

import math

from backend.app.core.models import GridState


def calculate_grid(symbol: str, base_price: float, current_price: float, step_size: float, x_level: int, tick_size: float) -> GridState:
    if step_size <= 0:
        raise ValueError("step_size must be > 0")
    if x_level < 1:
        raise ValueError("x_level must be >= 1")
    step_index = math.floor((current_price - base_price) / step_size)
    step_price = base_price + step_index * step_size
    upper_level = step_price + x_level * step_size
    lower_level = step_price - x_level * step_size
    step_distance = abs(current_price - step_price)
    return GridState(
        symbol=symbol,
        base_price=round(base_price, 8),
        current_price=round(current_price, 8),
        step_size=step_size,
        x_level=x_level,
        tick_size=tick_size,
        current_step=step_index,
        step_price=round(step_price, 8),
        upper_level=round(upper_level, 8),
        lower_level=round(lower_level, 8),
        step_distance=round(step_distance, 8),
    )
