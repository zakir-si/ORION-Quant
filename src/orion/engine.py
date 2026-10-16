"""Transparent daily-bar backtest engine with next-open execution."""
from __future__ import annotations

import pandas as pd

from orion.data import validate_prices
from orion.risk import daily_returns, max_drawdown, risk_flags


def run_backtest(prices: pd.DataFrame, target_signal: pd.Series, starting_cash: float = 100_000,
                 fee_rate: float = 0.001, slippage_rate: float = 0.0005,
                 max_position_fraction: float = 0.95,
                 max_drawdown_limit: float = 0.20,
                 max_daily_loss_limit: float = 0.05) -> dict[str, object]:
    """Run a long-only, one-asset simulation.

    The signal on day t changes the position at day t+1 open. Fractional
    shares are allowed for learning. Costs are charged on traded notional.
    """
    data = validate_prices(prices)
    if starting_cash <= 0:
        raise ValueError("starting_cash must be positive.")
    if fee_rate < 0 or slippage_rate < 0:
        raise ValueError("Fees and slippage cannot be negative.")
    if not 0 < max_position_fraction <= 1:
        raise ValueError("max_position_fraction must be in (0, 1].")
    signal = target_signal.reindex(data.index).fillna(0).clip(0, 1).astype(int)
    cash, shares = float(starting_cash), 0.0
    rows, trades = [], []

    for i, (date, bar) in enumerate(data.iterrows()):
        open_price, close_price = float(bar["Open"]), float(bar["Close"])
        target = int(signal.iloc[i - 1]) if i > 0 else 0
        equity_at_open = cash + shares * open_price
        # Only trade when entering or exiting. Do not rebalance every day.
        if target == 1 and shares <= 1e-10:
            desired_shares = max(0.0, equity_at_open * max_position_fraction / open_price)
        elif target == 0:
            desired_shares = 0.0
        else:
            desired_shares = shares
        change = desired_shares - shares

        if abs(change) > 1e-10:
            execution_price = open_price * (1 + slippage_rate if change > 0 else 1 - slippage_rate)
            if change > 0:
                affordable = max(0.0, cash / (execution_price * (1 + fee_rate)))
                change = min(change, affordable)
                notional = change * execution_price
                fee = notional * fee_rate
                shares += change
                cash -= notional + fee
                side = "BUY"
            else:
                change = max(change, -shares)
                notional = abs(change) * execution_price
                fee = notional * fee_rate
                shares += change
                cash += notional - fee
                side = "SELL"
            if abs(change) > 1e-10:
                trades.append({"Date": date, "Side": side, "Shares": abs(change),
                               "Price": execution_price, "Fees": fee})

        equity = cash + shares * close_price
        rows.append({"Date": date, "Open": open_price, "Close": close_price,
                     "Target": target, "Cash": cash, "Shares": shares, "Equity": equity})

    ledger = pd.DataFrame(rows).set_index("Date")
    returns = daily_returns(ledger["Equity"])
    drawdown = max_drawdown(ledger["Equity"])
    invested_value = ledger["Shares"] * data["Close"]
    position_fraction = invested_value / ledger["Equity"].replace(0, float("nan"))
    max_fraction = float(position_fraction.max()) if not position_fraction.empty else 0.0
    flags = risk_flags(returns, drawdown, max_fraction, max_drawdown_limit,
                       max_daily_loss_limit, max_position_fraction)
    return {
        "ledger": ledger,
        "trades": pd.DataFrame(trades, columns=["Date", "Side", "Shares", "Price", "Fees"]),
        "returns": returns,
        "max_drawdown": drawdown,
        "risk_flags": flags,
        "starting_cash": float(starting_cash),
        "ending_equity": float(ledger["Equity"].iloc[-1]),
        "max_position_fraction": max_fraction,
    }
