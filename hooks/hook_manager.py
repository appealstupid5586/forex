from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

from .schemas import HookContext, SignalHookResult, TradeHookResult, CloseHookResult

SignalHook = Callable[[HookContext], SignalHookResult]
TradeHook = Callable[[HookContext], TradeHookResult]
CloseHook = Callable[[HookContext], CloseHookResult]


class HookManager:
    def __init__(self, hooks_directory: str | Path | None = None):
        self.hooks_directory = Path(hooks_directory) if hooks_directory else Path(__file__).resolve().parent
        self.before_signal_hooks: list[SignalHook] = []
        self.after_signal_hooks: list[SignalHook] = []
        self.before_trade_hooks: list[TradeHook] = []
        self.after_trade_hooks: list[TradeHook] = []
        self.before_close_hooks: list[CloseHook] = []
        self.after_close_hooks: list[CloseHook] = []
        self.after_backtest_hooks: list[SignalHook] = []
        self._discover_hooks()

    def _discover_hooks(self) -> None:
        self.before_signal_hooks = self._load_hooks(self.hooks_directory / "before_signal", "before_signal_hook")
        self.after_signal_hooks = self._load_hooks(self.hooks_directory / "after_signal", "after_signal_hook")
        self.before_trade_hooks = self._load_hooks(self.hooks_directory / "before_trade", "before_trade_hook")
        self.after_trade_hooks = self._load_hooks(self.hooks_directory / "after_trade", "after_trade_hook")
        self.before_close_hooks = self._load_hooks(self.hooks_directory / "before_close", "before_close_hook")
        self.after_close_hooks = self._load_hooks(self.hooks_directory / "after_close", "after_close_hook")
        self.after_backtest_hooks = self._load_hooks(self.hooks_directory / "after_backtest", "after_backtest_hook")

    def run_before_signal(self, context: HookContext) -> list[SignalHookResult]:
        return [hook(context) for hook in self.before_signal_hooks]

    def run_after_signal(self, context: HookContext) -> list[SignalHookResult]:
        return [hook(context) for hook in self.after_signal_hooks]

    def run_before_trade(self, context: HookContext) -> list[TradeHookResult]:
        return [hook(context) for hook in self.before_trade_hooks]

    def run_after_trade(self, context: HookContext) -> list[TradeHookResult]:
        return [hook(context) for hook in self.after_trade_hooks]

    def run_before_close(self, context: HookContext) -> list[CloseHookResult]:
        return [hook(context) for hook in self.before_close_hooks]

    def run_after_close(self, context: HookContext) -> list[CloseHookResult]:
        return [hook(context) for hook in self.after_close_hooks]

    def run_after_backtest(self, context: HookContext) -> list[SignalHookResult]:
        return [hook(context) for hook in self.after_backtest_hooks]

    def register_before_signal_hook(self, hook: SignalHook) -> None:
        self.before_signal_hooks.append(hook)

    def register_after_signal_hook(self, hook: SignalHook) -> None:
        self.after_signal_hooks.append(hook)

    def register_before_trade_hook(self, hook: TradeHook) -> None:
        self.before_trade_hooks.append(hook)

    def register_after_trade_hook(self, hook: TradeHook) -> None:
        self.after_trade_hooks.append(hook)

    def register_before_close_hook(self, hook: CloseHook) -> None:
        self.before_close_hooks.append(hook)

    def register_after_close_hook(self, hook: CloseHook) -> None:
        self.after_close_hooks.append(hook)

    def register_after_backtest_hook(self, hook: SignalHook) -> None:
        self.after_backtest_hooks.append(hook)

    def _load_hooks(self, folder: Path, hook_name: str) -> list[Callable[[HookContext], Any]]:
        hooks: list[Callable[[HookContext], Any]] = []
        if not folder.exists():
            return hooks
        for path in sorted(folder.glob("*.py")):
            if path.name == "__init__.py":
                continue
            module_name = f"hooks.{folder.name}.{path.stem}"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            if hasattr(module, hook_name):
                hook = getattr(module, hook_name)
                if callable(hook):
                    hooks.append(hook)
        return hooks
