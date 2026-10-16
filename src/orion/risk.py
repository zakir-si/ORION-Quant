"""Risk calculations and simple safety guardrails."""
from __future__ import annotations

import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough fall, returned as a negative fraction."""
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def daily_returns(equity: pd.Series) -> pd.Series:
    """Daily equity returns, with the first undefined return set to zero."""
    return equity.pct_change().replace([float("inf"), -float("inf")], 0).fillna(0)


def risk_flags(returns: pd.Series, drawdown: float, position_fraction: float,
               max_drawdown_limit: float = 0.20, max_daily_loss_limit: float = 0.05,
               max_position_fraction: float = 0.95) -> list[str]:
    """Return warnings; this cannot guarantee protection from losses."""
    flags = []
    worst_day = float(returns.min()) if not returns.empty else 0.0
    if drawdown <= -abs(max_drawdown_limit):
        flags.append(f"Drawdown limit reached: {drawdown:.1%}")
    if worst_day <= -abs(max_daily_loss_limit):
        flags.append(f"Daily loss limit reached: {worst_day:.1%}")
    if position_fraction > max_position_fraction + 1e-6:
        flags.append(f"Position size is above the {max_position_fraction:.0%} guardrail")
    if not flags:
        flags.append("No configured risk threshold was breached in this run")
    return flags
