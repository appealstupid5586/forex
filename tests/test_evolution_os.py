from hooks.hook_manager import HookManager
from hooks.schemas import HookContext, SignalHookResult, TradeHookResult


def test_hook_manager_registers_and_runs_hooks():
    manager = HookManager()

    def before_signal(context: HookContext) -> SignalHookResult:
        return SignalHookResult(proceed=True, reasons=[f"before_signal:{context.event}"])

    def before_trade(context: HookContext) -> TradeHookResult:
        return TradeHookResult(proceed=False, reasons=["before_trade blocked"])

    manager.register_before_signal_hook(before_signal)
    manager.register_before_trade_hook(before_trade)

    signal_results = manager.run_before_signal(HookContext(event="signal_check", payload={"foo": "bar"}))
    trade_results = manager.run_before_trade(HookContext(event="trade_check", payload={"order_id": 1}))

    assert len(signal_results) == 1
    assert signal_results[0].proceed is True
    assert "before_signal:signal_check" in signal_results[0].reasons

    assert len(trade_results) == 1
    assert trade_results[0].proceed is False
    assert "before_trade blocked" in trade_results[0].reasons
