from orion.data import make_demo_prices
from orion.engine import run_backtest
from orion.strategies import buy_and_hold_signal


def test_backtest_returns_complete_ledger():
    prices = make_demo_prices(days=80, seed=5)
    result = run_backtest(prices, buy_and_hold_signal(prices["Close"]))
    assert len(result["ledger"]) == len(prices)
    assert {"Cash", "Shares", "Equity"}.issubset(result["ledger"].columns)
    assert result["ending_equity"] > 0


def test_first_bar_does_not_use_same_close_signal():
    prices = make_demo_prices(days=10)
    result = run_backtest(prices, buy_and_hold_signal(prices["Close"]))
    assert result["ledger"]["Shares"].iloc[0] == 0
    assert result["ledger"]["Shares"].iloc[1] > 0
