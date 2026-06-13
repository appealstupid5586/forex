from hooks.schemas import HookContext, SignalHookResult


def after_close_hook(context: HookContext) -> SignalHookResult:
    return SignalHookResult(proceed=True, reasons=["after_close hook executed"])
