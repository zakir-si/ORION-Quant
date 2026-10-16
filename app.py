"""ORION Quant dashboard. Run with: streamlit run app.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import plotly.graph_objects as go
import streamlit as st

from orion.data import download_prices, make_demo_prices
from orion.engine import run_backtest
from orion.reporting import summarize
from orion.strategies import buy_and_hold_signal, mean_reversion_signal, moving_average_signal

st.set_page_config(page_title="ORION Quant", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1020; color: #e8eefc; }
[data-testid="stMetric"] { background: #121a2d; padding: 14px; border: 1px solid #273450; border-radius: 12px; }
div[data-testid="stSidebar"] { background: #0e1628; }
</style>
""", unsafe_allow_html=True)
st.title("🛰️ ORION Quant")
st.caption("A transparent research lab for testing strategies — not a broker and not financial advice.")

with st.sidebar:
    st.header("Market data")
    source = st.radio("Source", ["Synthetic demo data", "Yahoo Finance daily data"])
    symbol = st.text_input("Ticker", "AAPL")
    period = st.selectbox("History", ["1y", "2y", "5y", "max"], index=1)
    st.divider()
    st.header("Strategy")
    strategy = st.selectbox("Rule", ["Moving average", "Mean reversion", "Buy & hold"])
    if strategy == "Moving average":
        fast = st.slider("Fast average", 3, 40, 10)
        slow = st.slider("Slow average", 15, 150, 40)
    else:
        fast, slow = 10, 40
    window = st.slider("Mean window", 5, 60, 20) if strategy == "Mean reversion" else 20
    st.divider()
    st.header("Simulation")
    starting_cash = st.number_input("Starting cash", min_value=100.0, value=100_000.0, step=5_000.0)
    fee_pct = st.number_input("Fee (%) per trade", min_value=0.0, max_value=2.0, value=0.10, step=0.05)
    slippage_pct = st.number_input("Slippage (%)", min_value=0.0, max_value=2.0, value=0.05, step=0.05)
    position_pct = st.slider("Maximum invested", 10, 100, 95) / 100
    replay_bars = st.slider("Historical replay cutoff (bars)", 30, 500, 500, 10)
    run = st.button("Run / refresh data", type="primary", use_container_width=True)

if "result" not in st.session_state:
    st.session_state.result = None
# Changing the replay slider recomputes the simulation at that historical point.
replay_changed = st.session_state.get("last_replay_bars") != replay_bars
if run or st.session_state.result is None or replay_changed:
    try:
        with st.spinner("Preparing prices and running the simulation..."):
            if source == "Synthetic demo data":
                all_prices = make_demo_prices(days=500)
                shown_symbol = "SYNTHETIC (not real market data)"
            else:
                all_prices = download_prices(symbol, period)
                shown_symbol = symbol.upper()
            prices = all_prices.iloc[:min(replay_bars, len(all_prices))].copy()
            close = prices["Close"]
            if strategy == "Moving average":
                signal = moving_average_signal(close, fast=fast, slow=slow)
            elif strategy == "Mean reversion":
                signal = mean_reversion_signal(close, window=window)
            else:
                signal = buy_and_hold_signal(close)
            result = run_backtest(prices, signal, starting_cash=starting_cash,
                                  fee_rate=fee_pct / 100, slippage_rate=slippage_pct / 100,
                                  max_position_fraction=position_pct)
            st.session_state.result = (prices, result, shown_symbol, strategy)
            st.session_state.last_replay_bars = replay_bars
    except Exception as exc:
        st.error(f"Could not run the simulation: {exc}")
        st.stop()

prices, result, shown_symbol, used_strategy = st.session_state.result
st.caption(f"Showing historical replay: {shown_symbol} · {used_strategy} · {len(prices)} of up to 500 bars")
st.progress(min(1.0, len(prices) / 500), text="Historical replay progress — this is not a live market feed")
metrics = summarize(result)
cols = st.columns(4)
for col, key in zip(cols, ["Total return", "Annualized volatility", "Sharpe ratio (rf=0)", "Maximum drawdown"]):
    value = metrics[key]
    col.metric(key, f"{value:.2f}" if key.startswith("Sharpe") else f"{value:.2%}")
cols = st.columns(3)
cols[0].metric("Ending equity", f"{metrics['Ending equity']:,.2f}")
cols[1].metric("Trade count", int(metrics["Trade count"]))
cols[2].metric("Turnover / starting cash", f"{metrics['Turnover / starting cash']:.2f}x")

left, right = st.columns([2, 1])
with left:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices.index, y=prices["Close"], name="Close price", yaxis="y"))
    fig.add_trace(go.Scatter(x=result["ledger"].index, y=result["ledger"]["Equity"], name="Account equity", yaxis="y2"))
    fig.update_layout(title="Price and account equity", template="plotly_dark", height=470,
                      yaxis=dict(title="Price"),
                      yaxis2=dict(title="Equity", overlaying="y", side="right"),
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Risk guardrails")
    for flag in result["risk_flags"]:
        if flag.startswith("No configured"):
            st.success(flag)
        else:
            st.warning(flag)
    st.info("Risk flags are warnings, not guarantees. Gaps, bad data, and real execution can produce larger losses.")

st.subheader("Trade log")
trades = result["trades"]
if trades.empty:
    st.write("No trades were triggered for this period.")
else:
    st.dataframe(trades, use_container_width=True, hide_index=True)
st.download_button("Download trades CSV", trades.to_csv(index=False), "orion_trades.csv", "text/csv")
st.download_button("Download equity ledger CSV", result["ledger"].to_csv(), "orion_equity_ledger.csv", "text/csv")
with st.expander("View daily equity ledger"):
    st.dataframe(result["ledger"], use_container_width=True)
with st.expander("Research notes and limitations"):
    st.markdown("""
    - The strategy signal is delayed by one bar before execution at the next open.
    - Costs are charged on traded notional; fractional shares are allowed for learning.
    - Yahoo Finance is an unofficial third-party data source and can be delayed or incomplete.
    - This historical replay is not a live feed. No live orders are placed.
    - Never paste API keys or brokerage passwords into this app.
    - Test multiple periods and include realistic costs before drawing conclusions.
    """)
