from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from app.skills.portfolio_analysis.risk_matrix import assess_portfolio_risk


class PortfolioEngine:
    """Portfolio analysis engine with health, risk and metric scoring."""

    def __init__(self, holdings: List[Dict[str, Any]] | None = None, margin_usage: float = 0.0):
        self.holdings = holdings or []
        self.margin_usage = float(margin_usage or 0.0)

    def total_value(self) -> float:
        return float(sum(h.get("value", 0) for h in self.holdings))

    def _currency_pairs(self) -> Dict[str, List[str]]:
        pairs: Dict[str, List[str]] = {}
        for h in self.holdings:
            sym = str(h.get("symbol", ""))
            if len(sym) == 6 and sym.isalpha():
                pairs[sym] = [sym[:3], sym[3:]]
        return pairs

    def _sector_for_symbol(self, symbol: str) -> str:
        symbol = symbol.upper()
        if symbol in ("XAUUSD", "XAGUSD", "XAUJPY", "XAGJPY"):
            return "metals"
        if any(key in symbol for key in ("NAS100", "SP500", "DOW", "FTSE", "DAX")):
            return "indices"
        if len(symbol) == 6 and symbol.isalpha():
            return "forex"
        if any(key in symbol for key in ("BTC", "ETH", "LTC", "XRP")):
            return "crypto"
        return "other"

    def exposure_analysis(self) -> Dict[str, Any]:
        total = self.total_value()
        exposures: Dict[str, float] = {}
        currency_exposure: Dict[str, float] = defaultdict(float)
        for h in self.holdings:
            sym = str(h.get("symbol", "UNKNOWN"))
            exposure = round(float(h.get("value", 0)) / total, 4) if total > 0 else 0.0
            exposures[sym] = exposure
            if len(sym) == 6 and sym.isalpha():
                base, quote = sym[:3], sym[3:]
                currency_exposure[base] += exposure
                currency_exposure[quote] += exposure

        max_exposure = round(max(exposures.values()) if exposures else 0.0, 4)
        return {
            "total_value": total,
            "exposures": exposures,
            "currency_exposure": dict(currency_exposure),
            "max_exposure": max_exposure,
            "exposure_score": max_exposure,
            "margin_usage": self.margin_usage,
        }

    def diversification_analysis(self) -> Dict[str, Any]:
        exposures = self.exposure_analysis().get("exposures", {})
        concentration = max(exposures.values()) if exposures else 0.0
        hhi = sum((v ** 2) for v in exposures.values()) if exposures else 0.0
        diversification_score = round(max(0.0, 1.0 - hhi), 4)
        sector_exposure: Dict[str, float] = defaultdict(float)
        symbol_overlap: Dict[str, float] = defaultdict(float)
        for symbol, exposure in exposures.items():
            sector = self._sector_for_symbol(symbol)
            sector_exposure[sector] += exposure
            if len(symbol) == 6 and symbol.isalpha():
                symbol_overlap[symbol[:3]] += exposure
                symbol_overlap[symbol[3:]] += exposure
            else:
                symbol_overlap[symbol] += exposure

        sector_overlap = round(max(sector_exposure.values()) if sector_exposure else 0.0, 4)
        symbol_overlap_score = round(max(symbol_overlap.values()) if symbol_overlap else 0.0, 4)
        return {
            "n_positions": len(exposures),
            "concentration": round(concentration, 4),
            "hhi": round(hhi, 4),
            "diversification_score": diversification_score,
            "sector_overlap": sector_overlap,
            "symbol_overlap": symbol_overlap_score,
        }

    def correlation_analysis(self) -> Dict[str, Any]:
        try:
            import pandas as pd
            import numpy as np
        except Exception:
            return {"note": "pandas not available", "correlation_score": 0.0}

        price_series: Dict[str, Any] = {}
        for h in self.holdings:
            sym = h.get("symbol")
            prices = h.get("prices")
            if sym and isinstance(prices, (list, tuple)) and len(prices) > 1:
                price_series[sym] = pd.Series(prices, dtype=float)

        if len(price_series) < 2:
            return {"note": "not enough price series to compute correlation", "correlation_score": 0.0}

        df = pd.DataFrame(price_series)
        returns = df.pct_change().dropna()
        if returns.empty:
            return {"note": "insufficient data after returns calculation", "correlation_score": 0.0}

        corr = returns.corr()
        triu = corr.where(~np.tril(np.ones(corr.shape, dtype=bool)))
        abs_vals = triu.abs().values[np.triu_indices_from(triu.values, k=1)]
        correlation_score = float(round(float(abs_vals.mean()) if abs_vals.size else 0.0, 4))
        corr_dict = {col: corr[col].to_dict() for col in corr.columns}
        correlated_pairs = []
        for i, row in corr.iterrows():
            for j, value in row.items():
                if i != j and abs(value) >= 0.75:
                    pair = tuple(sorted((i, j)))
                    if pair not in correlated_pairs:
                        correlated_pairs.append(pair)
        correlation_pairs = [f"{a} ↔ {b}" for a, b in correlated_pairs]
        return {
            "correlation_matrix": corr_dict,
            "correlation_score": correlation_score,
            "correlation_pairs": correlation_pairs,
        }

    def concentration_analysis(self) -> Dict[str, Any]:
        exposures = self.exposure_analysis().get("exposures", {})
        concentration_score = round(max(exposures.values()) if exposures else 0.0, 4)
        return {"concentration_score": concentration_score}

    def health_score(self, metrics: Dict[str, Any]) -> int:
        concentration = float(metrics.get("concentration_score", 0.0))
        correlation = float(metrics.get("correlation_score", 0.0))
        diversification = float(metrics.get("diversification_score", 0.0))
        margin = float(metrics.get("margin_usage", 0.0))

        concentration = max(0.0, min(1.0, concentration))
        correlation = max(0.0, min(1.0, correlation))
        diversification = max(0.0, min(1.0, diversification))
        margin = max(0.0, min(1.0, margin))

        score = (
            (1.0 - concentration) * 0.35
            + (1.0 - correlation) * 0.25
            + diversification * 0.25
            + (1.0 - margin) * 0.15
        )
        return int(round(max(0.0, min(1.0, score)) * 100))

    def exposure_risk(self, exposure_score: float) -> str:
        if exposure_score < 0.25:
            return "LOW"
        if exposure_score < 0.5:
            return "MEDIUM"
        if exposure_score < 0.75:
            return "HIGH"
        return "CRITICAL"

    def correlation_risk(self, correlation_score: float) -> str:
        if correlation_score < 0.25:
            return "LOW"
        if correlation_score < 0.5:
            return "MEDIUM"
        if correlation_score < 0.75:
            return "HIGH"
        return "CRITICAL"

    def warnings(self, metrics: Dict[str, Any]) -> List[str]:
        warnings: List[str] = []
        if float(metrics.get("max_exposure", 0.0)) > 0.5:
            warnings.append("High exposure to a single position")
        if float(metrics.get("correlation_score", 0.0)) >= 0.75:
            warnings.append("Holdings have high correlation")
        if float(metrics.get("margin_usage", 0.0)) >= 0.75:
            warnings.append("Margin usage is elevated")
        if float(metrics.get("concentration_score", 0.0)) >= 0.75:
            warnings.append("Portfolio concentration is high")
        return warnings


def analyze_portfolio(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    engine = PortfolioEngine(
        portfolio.get("holdings", []),
        margin_usage=portfolio.get("margin_usage", 0.0),
    )
    exposure = engine.exposure_analysis()
    diversification = engine.diversification_analysis()
    correlation = engine.correlation_analysis()
    concentration = engine.concentration_analysis()

    metrics = {
        "total_exposure": exposure["total_value"],
        "margin_usage": engine.margin_usage,
        "exposure_score": exposure["exposure_score"],
        "max_exposure": exposure["max_exposure"],
        "correlation_score": correlation.get("correlation_score", 0.0),
        "diversification_score": diversification["diversification_score"],
        "concentration_score": concentration["concentration_score"],
        "portfolio_health_score": engine.health_score({
            "concentration_score": concentration["concentration_score"],
            "correlation_score": correlation.get("correlation_score", 0.0),
            "diversification_score": diversification["diversification_score"],
            "margin_usage": engine.margin_usage,
        }),
    }
    metrics["portfolio_health_score"] = int(metrics["portfolio_health_score"])
    risk_assessment = assess_portfolio_risk(metrics)

    def concentration_risk_level(score: float) -> str:
        if score < 0.25:
            return "LOW"
        if score < 0.5:
            return "MEDIUM"
        if score < 0.75:
            return "HIGH"
        return "CRITICAL"

    return {
        "health_score": metrics["portfolio_health_score"],
        "risk_level": risk_assessment["risk_level"],
        "exposure_score": int(round(metrics["exposure_score"] * 100)),
        "correlation_risk": engine.correlation_risk(metrics["correlation_score"]),
        "concentration_risk": concentration_risk_level(metrics["concentration_score"]),
        "warnings": engine.warnings(metrics),
        "metrics": metrics,
        "analysis": {
            "exposure": exposure,
            "diversification": diversification,
            "correlation": correlation,
            "concentration": concentration,
        },
        "risk_assessment": risk_assessment,
    }


# compatibility alias
run_portfolio_analysis = analyze_portfolio
