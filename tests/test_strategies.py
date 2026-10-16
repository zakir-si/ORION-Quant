import pandas as pd
import pytest

from orion.strategies import buy_and_hold_signal, mean_reversion_signal, moving_average_signal


def test_buy_and_hold_is_always_invested():
    assert buy_and_hold_signal(pd.Series([10, 11, 12])).tolist() == [1, 1, 1]


def test_moving_average_signal_is_binary():
    signal = moving_average_signal(pd.Series(range(1, 101), dtype=float), fast=3, slow=8)
    assert set(signal.unique()).issubset({0, 1})
    assert signal.iloc[-1] == 1


def test_moving_average_rejects_bad_windows():
    with pytest.raises(ValueError):
        moving_average_signal(pd.Series([1, 2, 3]), fast=10, slow=2)


def test_mean_reversion_signal_is_binary():
    close = pd.Series([100 + (i % 5) for i in range(100)], dtype=float)
    signal = mean_reversion_signal(close, window=10)
    assert set(signal.unique()).issubset({0, 1})
