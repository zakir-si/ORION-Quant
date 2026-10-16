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

def test_buy_and_hold_does_not_rebalance_every_day():
    prices = make_demo_prices(days=30, seed=11)
    result = run_backtest(prices, buy_and_hold_signal(prices["Close"]))
    assert len(result["trades"]) == 1


def test_trading_costs_reduce_equity_on_same_prices():
    prices = make_demo_prices(days=60, seed=12)
    prices.loc[:, "Open"] = 100.0
    prices.loc[:, "Close"] = 100.0
    prices.loc[:, "High"] = 101.0
    prices.loc[:, "Low"] = 99.0
    signal = buy_and_hold_signal(prices["Close"])
    free_result = run_backtest(prices, signal, fee_rate=0, slippage_rate=0)
    costly_result = run_backtest(prices, signal, fee_rate=0.01, slippage_rate=0.01)
    assert costly_result["ending_equity"] < free_result["ending_equity"]
