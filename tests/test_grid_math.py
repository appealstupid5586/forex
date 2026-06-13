from app.strategy.grid_math import calculate_grid


def test_grid_math_levels():
    grid = calculate_grid("EURUSD", 1.1000, 1.1032, 0.0010, 2, 0.00001)
    assert grid.current_step == 3
    assert grid.step_price == 1.103
    assert grid.upper_level == 1.105
    assert grid.lower_level == 1.101
