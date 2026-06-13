from backend.app.skills.hedge_engine.hedge_engine_module import HedgeEngine
from backend.app.core.models import RobotState, MarketTick, GridState


def demo():
    state = RobotState(robot_id='r1', symbol='EURUSD', broker='SIM', magic_number=42)
    tick = MarketTick(symbol='EURUSD', bid=1.1000, ask=1.1002)
    hedger = HedgeEngine(base_lot=0.01, max_exposure_lots=1.0)

    cycle = hedger.open_base_hedge(state, tick)
    print('Opened cycle id:', cycle.cycle_id)
    print('Buy orders:', len(cycle.buy_orders), 'Sell orders:', len(cycle.sell_orders))

    grid = GridState(symbol='EURUSD', base_price=1.1, current_price=1.1001, step_size=0.001, x_level=2, tick_size=0.00001, current_step=0, step_price=1.1, upper_level=1.102, lower_level=1.098, step_distance=0.0001)
    surplus = hedger.evaluate_surplus(state, cycle, grid, tick)
    print('Surplus orders generated:', len(surplus))


if __name__ == '__main__':
    demo()
