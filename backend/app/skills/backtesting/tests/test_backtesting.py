from backend.app.skills.backtesting import BacktestEngine, calculate_statistics, generate_report
from hooks.hook_manager import HookManager
from hooks.schemas import HookContext, SignalHookResult


def test_statistics_calculates_drawdown_and_profit_factor():
    stats = calculate_statistics(
        [
            {"profit": 100},
            {"profit": -50},
            {"profit": -50},
            {"profit": 200},
        ],
        starting_balance=1000,
    )

    assert stats["win_rate"] == 0.5
    assert stats["profit_factor"] == 3.0
    assert stats["max_drawdown"] > 0
    assert stats["consecutive_losses"] == 2


def test_backtest_discovers_regime_weakness():
    result = BacktestEngine().run(
        strategy={"name": "breakout"},
        market_data={
            "trades": [
                {"profit": 200, "regime": "Trending"},
                {"profit": -150, "regime": "Low Liquidity"},
                {"profit": -50, "regime": "Low Liquidity"},
            ]
        },
        config={"starting_balance": 1000},
    )

    assert result["best_regime"] == "Trending"
    assert result["worst_regime"] == "Low Liquidity"
    assert "weak_regime:Low Liquidity" in result["weaknesses"]
    assert result["evidence"][0]["strategy"] == "breakout"


def test_report_generation_includes_recommendations():
    report = generate_report(
        {
            "win_rate": 0.4,
            "profit_factor": 0.9,
            "max_drawdown": 12,
            "statistics": {"trade_count": 10, "profit_factor": 0.9, "max_drawdown": 12},
            "regime_analysis": {"by_regime": {}},
            "equity_curve": [1000, 950],
            "drawdown_curve": [0, 5],
        }
    )

    assert "high_drawdown" in report["weaknesses"]
    assert report["recommendations"]


def test_after_backtest_hook_registration():
    manager = HookManager()
    manager.after_backtest_hooks.clear()

    def after_backtest_hook(context: HookContext) -> SignalHookResult:
        return SignalHookResult(proceed=True, reasons=[context.event], metadata={"kind": "backtest"})

    manager.register_after_backtest_hook(after_backtest_hook)
    results = manager.run_after_backtest(HookContext(event="after_backtest", payload={"ok": True}))

    assert len(results) == 1
    assert results[0].reasons == ["after_backtest"]
    assert results[0].metadata == {"kind": "backtest"}
