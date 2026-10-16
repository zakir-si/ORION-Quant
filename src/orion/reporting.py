"""Summary metrics for a completed backtest."""
from __future__ import annotations

import math


def summarize(result: dict[str, object], periods_per_year: int = 252) -> dict[str, float]:
    ledger = result["ledger"]
    returns = result["returns"]
    start, end = float(result["starting_cash"]), float(result["ending_equity"])
    total_return = end / start - 1
    count = max(1, len(returns) - 1)
    annual_return = (end / start) ** (periods_per_year / count) - 1 if end > 0 else -1.0
    volatility = float(returns.std(ddof=1) * math.sqrt(periods_per_year)) if len(returns) > 1 else 0.0
    daily_std = float(returns.std(ddof=1)) if len(returns) > 1 else 0.0
    sharpe = float(returns.mean() / daily_std * math.sqrt(periods_per_year)) if daily_std > 0 else 0.0
    trades = result["trades"]
    turnover = float((trades["Shares"] * trades["Price"]).sum() / start) if not trades.empty else 0.0
    return {
        "Total return": float(total_return),
        "Annualized return": float(annual_return),
        "Annualized volatility": volatility,
        "Sharpe ratio (rf=0)": sharpe,
        "Maximum drawdown": float(result["max_drawdown"]),
        "Ending equity": end,
        "Trade count": float(len(trades)),
        "Turnover / starting cash": turnover,
    }
