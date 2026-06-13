from hooks.schemas import HookContext, SignalHookResult


def before_close_hook(context: HookContext) -> SignalHookResult:
    return SignalHookResult(proceed=True, reasons=["before_close hook executed"])
