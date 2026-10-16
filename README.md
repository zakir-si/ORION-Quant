# ORION Quant

ORION is a learning-first quantitative research and paper-trading simulator. It tests simple strategies on daily stock prices, includes trading costs, reports risk, and replays historical bars in a dashboard.

> **Safety note:** ORION is educational software, not financial advice. It does not place real orders or connect to a broker. Backtests are not predictions, and a strategy that looked good in the past can lose money in the future.

## Features
- Streamlit dashboard with Buy & Hold, moving-average crossover, and mean-reversion strategies.
- Synthetic demo data that works offline, plus optional daily prices from yfinance.
- Long-only daily-bar backtest with next-open execution, fees, slippage, and cash/equity ledger.
- Risk checks for drawdown, daily loss, position sizing, and leverage.
- Return, volatility, Sharpe ratio, drawdown, trade log, and CSV downloads.
- Automated tests and GitHub Actions CI.

## Run locally
Use Python 3.10 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Start with **Synthetic demo data** to verify the app works offline. For market data, try `AAPL` or `RELIANCE.NS`.

## Tests
```bash
python -m pytest -q
```

## Code map
- `app.py`: dashboard and controls.
- `src/orion/data.py`: data loading and validation.
- `src/orion/strategies.py`: simple strategy rules.
- `src/orion/engine.py`: backtest loop and ledger.
- `src/orion/risk.py`: risk guardrails and statistics.
- `src/orion/reporting.py`: summary metrics.
- `tests/`: automated tests.

## Assumptions and limitations
- One asset at a time, long-only, daily OHLCV bars.
- Signals use prior-close information and execute at the next open.
- No real brokerage execution, short selling, intraday order book, market impact, taxes, dividends, or full corporate-action handling.
- Risk checks are warnings, not a guarantee against losses.
- Backtests can still suffer from survivorship bias, overfitting, and data errors. Treat results as experiments, not investment advice.

Code is intentionally straightforward and commented so a student can learn from it.
