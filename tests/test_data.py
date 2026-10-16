import pandas as pd
import pytest

from orion.data import make_demo_prices, validate_prices


def test_demo_prices_are_valid_and_repeatable():
    first = make_demo_prices(days=50, seed=123)
    second = make_demo_prices(days=50, seed=123)
    pd.testing.assert_frame_equal(first, second)


def test_validator_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_prices(pd.DataFrame({"Close": [1, 2, 3]}))


def test_validator_rejects_too_few_rows():
    frame = make_demo_prices(days=3).iloc[:2]
    with pytest.raises(ValueError, match="At least three"):
        validate_prices(frame)
