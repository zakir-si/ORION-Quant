import pandas as pd

from orion.risk import max_drawdown, risk_flags


def test_max_drawdown_is_negative_for_a_fall():
    assert max_drawdown(pd.Series([100, 120, 90, 110])) == -0.25


def test_risk_flags_warn_on_large_drawdown_and_loss():
    flags = risk_flags(pd.Series([0.0, -0.06]), -0.25, 0.9)
    assert any("Drawdown limit reached" in flag for flag in flags)
    assert any("Daily loss limit reached" in flag for flag in flags)
