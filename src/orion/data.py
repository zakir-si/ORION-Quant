"""Data helpers for real daily prices and offline synthetic demo prices."""
from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def validate_prices(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a clean OHLCV frame or raise a clear error."""
    if frame is None or frame.empty:
        raise ValueError("No price rows were provided.")
    clean = frame.copy()
    if isinstance(clean.columns, pd.MultiIndex):
        clean.columns = clean.columns.get_level_values(0)
    missing = [column for column in REQUIRED_COLUMNS if column not in clean.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    clean = clean[REQUIRED_COLUMNS].copy()
    clean.index = pd.to_datetime(clean.index)
    clean = clean[~clean.index.duplicated(keep="last")].sort_index()
    for column in REQUIRED_COLUMNS:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
    clean = clean.dropna(subset=["Open", "High", "Low", "Close"])
    clean = clean[(clean[["Open", "High", "Low", "Close"]] > 0).all(axis=1)]
    if len(clean) < 3:
        raise ValueError("At least three valid daily bars are required.")
    if (clean["High"] < clean[["Open", "Close", "Low"]].max(axis=1)).any():
        raise ValueError("Some High values are lower than Open, Close, or Low.")
    if (clean["Low"] > clean[["Open", "Close", "High"]].min(axis=1)).any():
        raise ValueError("Some Low values are higher than Open, Close, or High.")
    clean["Volume"] = clean["Volume"].fillna(0).clip(lower=0)
    return clean


def make_demo_prices(days: int = 500, seed: int = 7, start_price: float = 100.0) -> pd.DataFrame:
    """Make reproducible synthetic OHLCV data. These are not real market prices."""
    if days < 3:
        raise ValueError("days must be at least 3.")
    if start_price <= 0:
        raise ValueError("start_price must be positive.")
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0003, scale=0.015, size=days)
    close = start_price * np.exp(np.cumsum(returns))
    open_prices = np.r_[start_price, close[:-1]] * (1 + rng.normal(0, 0.003, days))
    high = np.maximum(open_prices, close) * (1 + rng.uniform(0, 0.012, days))
    low = np.minimum(open_prices, close) * (1 - rng.uniform(0, 0.012, days))
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    frame = pd.DataFrame({
        "Open": open_prices, "High": high, "Low": low, "Close": close,
        "Volume": rng.integers(100_000, 2_000_000, days),
    }, index=dates)
    return validate_prices(frame)


def download_prices(symbol: str, period: str = "2y") -> pd.DataFrame:
    """Download daily prices from Yahoo Finance via yfinance (internet required)."""
    if not symbol or not symbol.strip():
        raise ValueError("Enter a ticker symbol.")
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install yfinance with: python -m pip install yfinance") from exc
    frame = yf.download(symbol.strip(), period=period, interval="1d", auto_adjust=True,
                        progress=False, threads=False)
    if frame is None or frame.empty:
        raise ValueError("No data returned. Check the ticker and internet connection.")
    return validate_prices(frame)
