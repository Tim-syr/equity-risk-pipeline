import transform
import pandas
import math
import pytest
import statistics


def test_add_drawdown():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 120.0, 90.0]})
    result = transform.add_drawdown(ticker_data)
    assert result["drawdown"].tolist() == [0.0, 0.0, -0.25]


def test_add_drawdown_two_tickers_keep_their_own_peak():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17",
                                             "2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 120.0, 90.0, 10.0, 5.0, 20.0]})
    result = transform.add_drawdown(ticker_data)
    assert result["drawdown"].tolist() == [0.0, 0.0, -0.25, 0.0, -0.5, 0.0]


def test_add_drawdown_unsorted_input():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-17", "2026-09-15", "2026-09-16"],
                                    "close": [90.0, 100.0, 120.0]})
    result = transform.add_drawdown(ticker_data)
    assert result["drawdown"].tolist() == [0.0, 0.0, -0.25]


def test_add_drawdown_does_not_modify_input():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 120.0, 90.0]})
    transform.add_drawdown(ticker_data)
    assert ticker_data.columns.tolist() == ["ticker", "date", "close"]


def test_add_drawdown_single_day():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"],
                                    "date": ["2026-09-15"],
                                    "close": [100.0]})
    result = transform.add_drawdown(ticker_data)
    assert result["drawdown"].tolist() == [0.0]


def test_add_drawdown_empty_dataframe():
    ticker_data = pandas.DataFrame({"ticker": pandas.Series([], dtype=str),
                                    "date": pandas.Series([], dtype=str),
                                    "close": pandas.Series([], dtype=float)})
    result = transform.add_drawdown(ticker_data)
    assert len(result) == 0
    assert "drawdown" in result.columns




def test_add_log_change_column():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 110.0, 99.0]})
    result = transform.add_log_change_column(ticker_data)
    expected = [float("nan"), math.log(110 / 100), math.log(99 / 110)]
    assert result["log_change"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_log_change_column_two_tickers_do_not_mix():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17",
                                             "2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 110.0, 99.0, 10.0, 20.0, 10.0]})
    result = transform.add_log_change_column(ticker_data)
    expected = [float("nan"), math.log(110 / 100), math.log(99 / 110),
                float("nan"), math.log(20 / 10), math.log(10 / 20)]
    assert result["log_change"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_log_change_column_unsorted_input():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-17", "2026-09-15", "2026-09-16"],
                                    "close": [99.0, 100.0, 110.0]})
    result = transform.add_log_change_column(ticker_data)
    expected = [float("nan"), math.log(110 / 100), math.log(99 / 110)]
    assert result["log_change"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_log_change_column_does_not_modify_input():
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-17"],
                                    "close": [100.0, 110.0, 99.0]})
    transform.add_log_change_column(ticker_data)
    assert ticker_data.columns.tolist() == ["ticker", "date", "close"]


def test_add_log_change_column_single_day():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"],
                                    "date": ["2026-09-15"],
                                    "close": [100.0]})
    result = transform.add_log_change_column(ticker_data)
    assert pandas.isna(result.loc[0, "log_change"])


def test_add_log_change_column_empty_dataframe():
    ticker_data = pandas.DataFrame({"ticker": pandas.Series([], dtype=str),
                                    "date": pandas.Series([], dtype=str),
                                    "close": pandas.Series([], dtype=float)})
    result = transform.add_log_change_column(ticker_data)
    assert len(result) == 0
    assert "log_change" in result.columns


def test_add_log_change_column_missing_day_in_the_middle():
    # documents the current behaviour: 2026-09-17 is missing, so the last log_change
    # silently covers two days (see the gap entry in docs/Known_issues.md)
    ticker_data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                                    "date": ["2026-09-15", "2026-09-16", "2026-09-18"],
                                    "close": [100.0, 110.0, 99.0]})
    result = transform.add_log_change_column(ticker_data)
    expected = [float("nan"), math.log(110 / 100), math.log(99 / 110)]
    assert result["log_change"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_volatility_21_days_constant_price():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 22,
                                    "date": pandas.date_range("2026-09-01", periods=22),
                                    "log_change": [float("nan")] + [0.0] * 21})
    result = transform.add_volatility_21_days(ticker_data)
    expected = [float("nan")] * 21 + [0.0]
    assert result["volatility_21"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_volatility_21_days_known_value():
    returns = [0.01, -0.01] * 10 + [0.03]
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 22,
                                    "date": pandas.date_range("2026-09-01", periods=22),
                                    "log_change": [float("nan")] + returns})
    result = transform.add_volatility_21_days(ticker_data)
    expected = [float("nan")] * 21 + [statistics.stdev(returns) * math.sqrt(252)]
    assert result["volatility_21"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_volatility_21_days_two_tickers_keep_their_own_window():
    # BBB's first return is not NaN on purpose: without groupby, BBB's windows would
    # reach back into AAA's rows and produce values too early
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 22 + ["BBB"] * 21,
                                    "date": list(pandas.date_range("2026-09-01", periods=22))
                                            + list(pandas.date_range("2026-09-01", periods=21)),
                                    "log_change": [float("nan")] + [0.0] * 21 + [0.02, -0.02] * 10 + [0.02]})
    result = transform.add_volatility_21_days(ticker_data)
    bbb = result[result["ticker"] == "BBB"]
    expected_bbb = [float("nan")] * 20 + [statistics.stdev([0.02, -0.02] * 10 + [0.02]) * math.sqrt(252)]
    assert bbb["volatility_21"].tolist() == pytest.approx(expected_bbb, nan_ok=True)


def test_add_volatility_21_days_not_enough_rows():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 21,
                                    "date": pandas.date_range("2026-09-01", periods=21),
                                    "log_change": [float("nan")] + [0.01] * 20})
    result = transform.add_volatility_21_days(ticker_data)
    assert result["volatility_21"].isna().all()


def test_add_volatility_21_days_unsorted_input():
    returns = [0.01, -0.01] * 10 + [0.03]
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 22,
                                    "date": pandas.date_range("2026-09-01", periods=22),
                                    "log_change": [float("nan")] + returns})
    shuffled = ticker_data.sample(frac=1, random_state=0)
    result = transform.add_volatility_21_days(shuffled)
    expected = [float("nan")] * 21 + [statistics.stdev(returns) * math.sqrt(252)]
    assert result["volatility_21"].tolist() == pytest.approx(expected, nan_ok=True)


def test_add_volatility_21_days_does_not_modify_input():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"] * 22,
                                    "date": pandas.date_range("2026-09-01", periods=22),
                                    "log_change": [float("nan")] + [0.0] * 21})
    transform.add_volatility_21_days(ticker_data)
    assert ticker_data.columns.tolist() == ["ticker", "date", "log_change"]


def test_add_volatility_21_days_single_day():
    ticker_data = pandas.DataFrame({"ticker": ["AAA"],
                                    "date": ["2026-09-15"],
                                    "log_change": [float("nan")]})
    result = transform.add_volatility_21_days(ticker_data)
    assert pandas.isna(result.loc[0, "volatility_21"])


def test_add_volatility_21_days_empty_dataframe():
    ticker_data = pandas.DataFrame({"ticker": pandas.Series([], dtype=str),
                                    "date": pandas.Series([], dtype=str),
                                    "log_change": pandas.Series([], dtype=float)})
    result = transform.add_volatility_21_days(ticker_data)
    assert len(result) == 0
    assert "volatility_21" in result.columns



def test_nan_to_null_replaces_nan_with_none():
    data = pandas.DataFrame({"ticker": ["AAA", "AAA"],
                             "log_change": [float("nan"), 0.05]})
    result = transform.nan_to_null(data)
    assert result.loc[0, "log_change"] is None
    assert result.loc[1, "log_change"] == 0.05
    assert result["ticker"].tolist() == ["AAA", "AAA"]


def test_nan_to_null_does_not_modify_input():
    data = pandas.DataFrame({"ticker": ["AAA", "AAA"],
                             "log_change": [float("nan"), 0.05]})
    transform.nan_to_null(data)
    assert pandas.isna(data.loc[0, "log_change"])
    assert data.loc[0, "log_change"] is not None


def test_nan_to_null_empty_dataframe():
    data = pandas.DataFrame({"ticker": pandas.Series([], dtype=str),
                             "log_change": pandas.Series([], dtype=float)})
    result = transform.nan_to_null(data)
    assert len(result) == 0
    assert result.columns.tolist() == ["ticker", "log_change"]





def test_add_daily_metrics():
    data = pandas.DataFrame({"ticker": ["AAA", "AAA", "AAA"],
                             "date": ["2026-09-15", "2026-09-16", "2026-09-17"],
                             "close": [100.0, 110.0, 99.0]})
    result = transform.add_daily_metrics(data)
    expected_log_change = [float("nan"), math.log(110 / 100), math.log(99 / 110)]
    assert result["log_change"].tolist() == pytest.approx(expected_log_change, nan_ok=True)
    assert result["drawdown"].tolist() == pytest.approx([0.0, 0.0, 99/110 -1])
    assert result["volatility_21"].isna().all()


def test_add_daily_metrics_empty_input():
    data = pandas.DataFrame({"ticker": pandas.Series([], dtype=str),
                             "date": pandas.Series([], dtype=str),
                             "close": pandas.Series([], dtype=float)})
    result = transform.add_daily_metrics(data)
    assert len(result) == 0
    assert list(result.columns) == ["ticker", "date", "close", "log_change", "volatility_21", "drawdown"]
