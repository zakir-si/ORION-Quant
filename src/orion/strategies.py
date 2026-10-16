"""Small, explainable strategy functions. A value of 1 means hold; 0 means cash."""
from __future__ import annotations

import pandas as pd


def moving_average_signal(close: pd.Series, fast: int = 20, slow: int = 50) -> pd.Series:
    """Be invested when the fast average is above the slow average."""
    if fast < 1 or slow < 2 or fast >= slow:
        raise ValueError("Use 1 <= fast < slow.")
    fast_avg = close.rolling(fast, min_periods=fast).mean()
    slow_avg = close.rolling(slow, min_periods=slow).mean()
    return (fast_avg > slow_avg).fillna(False).astype(int)


def mean_reversion_signal(close: pd.Series, window: int = 20, entry_z: float = -1.5,
                          exit_z: float = -0.2) -> pd.Series:
    """Enter below a rolling mean and exit after a recovery threshold."""
    if window < 2:
        raise ValueError("window must be at least 2.")
    if entry_z >= exit_z:
        raise ValueError("entry_z must be less than exit_z.")
    mean = close.rolling(window, min_periods=window).mean()
    std = close.rolling(window, min_periods=window).std(ddof=0).replace(0, float("nan"))
    z_score = (close - mean) / std
    signal = []
    invested = 0
    for value in z_score:
        if pd.isna(value):
            invested = 0
        elif value <= entry_z:
            invested = 1
        elif value >= exit_z:
            invested = 0
        signal.append(invested)
    return pd.Series(signal, index=close.index, dtype=int)


def buy_and_hold_signal(close: pd.Series) -> pd.Series:
    """Hold after the first available close."""
    return pd.Series(1, index=close.index, dtype=int)
