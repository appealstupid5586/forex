from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.models import HedgeCycle, Order, RobotState, WinnerGene


class JsonStateStore:
    """Small durable JSON store for MVP.

    Replace this with Postgres + Redis when moving beyond MVP.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = Lock()
        if not self.path.exists():
            self.path.write_text(json.dumps({"robot": None, "cycles": {}, "orders": {}}, indent=2), encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        with self._lock:
            self.path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def save_robot(self, state: RobotState) -> None:
        data = self._read()
        data["robot"] = state.model_dump(mode="json")
        self._write(data)

    def load_robot(self) -> RobotState | None:
        data = self._read()
        return RobotState.model_validate(data["robot"]) if data.get("robot") else None

    def save_cycle(self, cycle: HedgeCycle) -> None:
        data = self._read()
        data.setdefault("cycles", {})[cycle.cycle_id] = cycle.model_dump(mode="json")
        for order in cycle.buy_orders + cycle.sell_orders:
            data.setdefault("orders", {})[order.order_id] = order.model_dump(mode="json")
        self._write(data)

    def load_cycle(self, cycle_id: str) -> HedgeCycle | None:
        data = self._read()
        raw = data.get("cycles", {}).get(cycle_id)
        return HedgeCycle.model_validate(raw) if raw else None

    def all_orders(self) -> list[Order]:
        data = self._read()
        return [Order.model_validate(x) for x in data.get("orders", {}).values()]


class GeneStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def list(self) -> list[WinnerGene]:
        with self._lock:
            return [WinnerGene.model_validate(x) for x in json.loads(self.path.read_text(encoding="utf-8"))]

    def add(self, gene: WinnerGene) -> None:
        items = self.list()
        items.append(gene)
        with self._lock:
            self.path.write_text(json.dumps([x.model_dump(mode="json") for x in items], indent=2), encoding="utf-8")

    def promote(self, symbol: str, timeframe: str) -> WinnerGene | None:
        items = self.list()
        candidates = [g for g in items if g.symbol == symbol and g.timeframe == timeframe]
        if not candidates:
            return None
        best = sorted(candidates, key=lambda g: (g.profit_factor, g.recovery_factor, -g.max_drawdown), reverse=True)[0]
        for g in items:
            if g.symbol == symbol and g.timeframe == timeframe:
                g.promoted = g is best or (g.step_size == best.step_size and g.x_level == best.x_level)
        with self._lock:
            self.path.write_text(json.dumps([x.model_dump(mode="json") for x in items], indent=2), encoding="utf-8")
        return best
