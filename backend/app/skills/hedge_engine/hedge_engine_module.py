from __future__ import annotations

from backend.app.core.models import GridState, HedgeCycle, MarketTick, Order, OrderSide, RobotState


class HedgeEngine:
    def __init__(self, base_lot: float, max_exposure_lots: float):
        self.base_lot = base_lot
        self.max_exposure_lots = max_exposure_lots

    def open_base_hedge(self, state: RobotState, tick: MarketTick) -> HedgeCycle:
        cycle = HedgeCycle(symbol=state.symbol)
        buy = Order(robot_id=state.robot_id, cycle_id=cycle.cycle_id, symbol=state.symbol, side=OrderSide.BUY, lot=self.base_lot, entry_price=tick.ask, magic_number=state.magic_number)
        sell = Order(robot_id=state.robot_id, cycle_id=cycle.cycle_id, symbol=state.symbol, side=OrderSide.SELL, lot=self.base_lot, entry_price=tick.bid, magic_number=state.magic_number)
        cycle.buy_orders.append(buy)
        cycle.sell_orders.append(sell)
        cycle.hedge_ratio = 1.0
        return cycle

    def evaluate_surplus(self, state: RobotState, cycle: HedgeCycle, grid: GridState, tick: MarketTick) -> list[Order]:
        orders: list[Order] = []
        total_lots = sum(o.lot for o in cycle.buy_orders + cycle.sell_orders)
        if total_lots + self.base_lot > self.max_exposure_lots:
            return orders
        if tick.mid >= grid.upper_level:
            cycle.surplus_side = "BUY"
            orders.append(Order(robot_id=state.robot_id, cycle_id=cycle.cycle_id, symbol=state.symbol, side=OrderSide.BUY, lot=self.base_lot, entry_price=tick.ask, magic_number=state.magic_number))
        elif tick.mid <= grid.lower_level:
            cycle.surplus_side = "SELL"
            orders.append(Order(robot_id=state.robot_id, cycle_id=cycle.cycle_id, symbol=state.symbol, side=OrderSide.SELL, lot=self.base_lot, entry_price=tick.bid, magic_number=state.magic_number))
        else:
            cycle.surplus_side = "NONE"
        return orders
