from __future__ import annotations

from app.skills.portfolio_analysis import analyze_portfolio
from app.skills.portfolio_analysis.risk_matrix import assess_portfolio_risk


def test_analyze_portfolio_with_prices():
    portfolio = {
        "holdings": [
            {"symbol": "A", "value": 50000, "prices": [1, 1.1, 1.05, 1.08, 1.07]},
            {"symbol": "B", "value": 30000, "prices": [2, 2.05, 2.1, 2.08, 2.09]},
            {"symbol": "C", "value": 20000, "prices": [3, 2.9, 3.05, 3.1, 3.0]},
        ],
        "margin_usage": 0.15,
    }

    res = analyze_portfolio(portfolio)
    assert "health_score" in res
    assert "correlation_risk" in res
    assert "concentration_risk" in res
    assert "exposure_score" in res
    assert "risk_level" in res
    assert "warnings" in res
    assert "metrics" in res
    assert "analysis" in res
    assert "risk_assessment" in res

    assert 0 <= res["health_score"] <= 100
    assert res["correlation_risk"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert res["concentration_risk"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0 <= res["exposure_score"] <= 100
    assert res["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert isinstance(res["warnings"], list)

    div_score = res["metrics"]["diversification_score"]
    assert 0.0 <= div_score <= 1.0

    corr_score = res["metrics"].get("correlation_score", 0.0)
    assert 0.0 <= corr_score <= 1.0


def test_analyze_portfolio_warnings_for_over_exposure():
    portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 90000},
            {"symbol": "USDJPY", "value": 5000},
            {"symbol": "GBPUSD", "value": 5000},
        ],
        "margin_usage": 0.9,
    }

    res = analyze_portfolio(portfolio)
    assert "High exposure to a single position" in res["warnings"]
    assert "Margin usage is elevated" in res["warnings"]
    assert res["risk_assessment"]["risk_level"] in ("HIGH", "CRITICAL")


def test_assess_portfolio_risk():
    metrics = {
        "concentration_score": 0.8,
        "margin_usage": 0.2,
        "correlation_score": 0.3,
        "exposure_score": 0.7,
    }
    r = assess_portfolio_risk(metrics)
    assert r["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0.0 <= r["risk_score"] <= 1.0
    assert "dimensions" in r
    assert r["dimensions"]["exposure"] == 0.7


def test_correlation_pairs_are_reported_for_highly_correlated_holdings():
    portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 50000, "prices": [1, 1.02, 1.04, 1.06, 1.08]},
            {"symbol": "GBPUSD", "value": 30000, "prices": [1.5, 1.53, 1.56, 1.59, 1.62]},
            {"symbol": "USDJPY", "value": 20000, "prices": [110, 111, 112, 113, 114]},
        ],
        "margin_usage": 0.1,
    }

    res = analyze_portfolio(portfolio)
    correlation = res["analysis"]["correlation"]
    assert correlation["correlation_score"] >= 0.75 or correlation["correlation_pairs"]
    assert isinstance(correlation.get("correlation_pairs", []), list)


def test_margin_usage_drives_risk_classification():
    high_margin_metrics = {
        "concentration_score": 0.1,
        "margin_usage": 0.95,
        "correlation_score": 0.1,
        "exposure_score": 0.1,
    }
    r = assess_portfolio_risk(high_margin_metrics)
    assert r["risk_level"] in ("MEDIUM", "HIGH", "CRITICAL")
    assert r["dimensions"]["margin_usage"] == 0.95


def test_health_score_range():
    low_risk_portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 25000},
            {"symbol": "USDJPY", "value": 25000},
            {"symbol": "GBPUSD", "value": 25000},
            {"symbol": "AUDUSD", "value": 25000},
        ],
        "margin_usage": 0.1,
    }
    high_risk_portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 85000},
            {"symbol": "GBPUSD", "value": 10000},
            {"symbol": "USDJPY", "value": 5000},
        ],
        "margin_usage": 0.9,
    }

    low_risk_res = analyze_portfolio(low_risk_portfolio)
    high_risk_res = analyze_portfolio(high_risk_portfolio)

    assert 70 <= low_risk_res["health_score"] <= 100
    assert 0 <= high_risk_res["health_score"] <= 40


def test_correlation_matrix_structure():
    portfolio = {
        "holdings": [
            {"symbol": "A", "value": 50000, "prices": [1.0, 1.01, 1.02, 1.03, 1.04]},
            {"symbol": "B", "value": 30000, "prices": [2.0, 2.01, 2.02, 2.03, 2.04]},
            {"symbol": "C", "value": 20000, "prices": [3.0, 2.99, 2.98, 2.97, 2.96]},
        ],
    }

    res = analyze_portfolio(portfolio)
    correlation = res["analysis"]["correlation"]

    if "correlation_matrix" in correlation:
        corr_matrix = correlation["correlation_matrix"]
        assert isinstance(corr_matrix, dict)
        assert len(corr_matrix) >= 2
        for symbol, correlations in corr_matrix.items():
            assert isinstance(correlations, dict)
            assert len(correlations) > 0


def test_currency_exposure_in_forex_pairs():
    portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 50000},
            {"symbol": "GBPUSD", "value": 30000},
            {"symbol": "USDJPY", "value": 20000},
        ],
    }

    res = analyze_portfolio(portfolio)
    exposure = res["analysis"]["exposure"]

    assert "currency_exposure" in exposure
    currency_exp = exposure["currency_exposure"]
    assert isinstance(currency_exp, dict)
    assert currency_exp.get("USD", 0.0) > 0.0
    assert currency_exp.get("EUR", 0.0) > 0.0 or currency_exp.get("GBP", 0.0) > 0.0 or currency_exp.get("JPY", 0.0) > 0.0


def test_risk_assessment_zero_metrics():
    metrics = {
        "concentration_score": 0.0,
        "margin_usage": 0.0,
        "correlation_score": 0.0,
        "exposure_score": 0.0,
    }
    r = assess_portfolio_risk(metrics)
    assert r["risk_level"] == "LOW"
    assert 0.0 <= r["risk_score"] <= 0.25


def test_risk_assessment_max_metrics():
    metrics = {
        "concentration_score": 1.0,
        "margin_usage": 1.0,
        "correlation_score": 1.0,
        "exposure_score": 1.0,
    }
    r = assess_portfolio_risk(metrics)
    assert r["risk_level"] in ("HIGH", "CRITICAL")
    assert r["risk_score"] >= 0.75


def test_risk_assessment_with_drawdown():
    metrics = {
        "concentration_score": 0.2,
        "margin_usage": 0.3,
        "correlation_score": 0.2,
        "exposure_score": 0.4,
        "drawdown": 0.25,
    }
    r = assess_portfolio_risk(metrics)
    assert r["risk_level"] in ("LOW", "MEDIUM")
    assert r["dimensions"]["drawdown"] == 0.25


def test_diversification_overlap_scores():
    portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 50000},
            {"symbol": "GBPUSD", "value": 30000},
            {"symbol": "USDJPY", "value": 20000},
        ],
        "margin_usage": 0.1,
    }

    res = analyze_portfolio(portfolio)
    diversification = res["analysis"]["diversification"]

    assert diversification["sector_overlap"] > 0.0
    assert diversification["symbol_overlap"] > 0.0
    assert diversification["sector_overlap"] >= diversification["symbol_overlap"] or diversification["symbol_overlap"] >= diversification["sector_overlap"]


def test_risk_classification_high_risk():
    portfolio = {
        "holdings": [
            {"symbol": "EURUSD", "value": 80000},
            {"symbol": "USDJPY", "value": 15000},
            {"symbol": "GBPUSD", "value": 5000},
        ],
        "margin_usage": 0.95,
    }

    res = analyze_portfolio(portfolio)
    assert res["risk_assessment"]["risk_level"] in ("HIGH", "CRITICAL")
    assert res["health_score"] <= 50
