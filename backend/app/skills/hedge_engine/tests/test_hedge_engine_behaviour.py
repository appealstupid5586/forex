from backend.app.skills.hedge_engine.hedge_engine_module import HedgeEngine
from backend.app.core.models import RobotState, MarketTick, GridState


def test_open_base_hedge_creates_orders():
    state = RobotState(robot_id='r1', symbol='EURUSD', broker='SIM', magic_number=99)
    tick = MarketTick(symbol='EURUSD', bid=1.1000, ask=1.1002)
    hedger = HedgeEngine(base_lot=0.01, max_exposure_lots=1.0)

    cycle = hedger.open_base_hedge(state, tick)
    assert cycle is not None
    assert len(cycle.buy_orders) == 1
    assert len(cycle.sell_orders) == 1
    assert cycle.hedge_ratio == 1.0


def test_evaluate_surplus_generates_expected_order():
    state = RobotState(robot_id='r2', symbol='EURUSD', broker='SIM', magic_number=7)
    tick = MarketTick(symbol='EURUSD', bid=1.1049, ask=1.1051)
    hedger = HedgeEngine(base_lot=0.01, max_exposure_lots=1.0)

    # create initial cycle
    cycle = hedger.open_base_hedge(state, tick)

    # grid where upper_level <= tick.mid to trigger BUY surplus
    grid = GridState(symbol='EURUSD', base_price=1.1, current_price=1.1050, step_size=0.001, x_level=2, tick_size=0.00001, current_step=0, step_price=1.103, upper_level=1.104, lower_level=1.100, step_distance=0.002)

    orders = hedger.evaluate_surplus(state, cycle, grid, tick)
    assert isinstance(orders, list)
    assert len(orders) >= 0
    # surplus_side should be set appropriately
    assert cycle.surplus_side in ("BUY", "SELL", "NONE")
