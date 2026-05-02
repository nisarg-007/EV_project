import pandas as pd
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

PARQUET_PATH = "data/processed/Electric_Vehicle_Population_Data.parquet"


def _mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    mask = actual != 0
    if mask.sum() == 0:
        return float("inf")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


class EVForecaster:
    """
    Forecasts county-level EV registration growth using Prophet (primary)
    with ARIMA(1,1,1) fallback for sparse counties (< 24 data points).
    """

    def __init__(self):
        self._model = None
        self._model_name: str = ""
        self._fitted = False
        self._last_date: Optional[pd.Timestamp] = None
        self._freq: str = "YE"

    def fit(self, df: pd.DataFrame, county: str) -> "EVForecaster":
        county_df = df[df["county"] == county].copy() if "county" in df.columns else df.copy()
        if county_df.empty:
            raise ValueError(f"No data for county: {county}")

        ts = (
            county_df.sort_values("date")
            .rename(columns={"date": "ds", "registrations": "y"})
            [["ds", "y"]]
            .dropna()
        )
        ts["ds"] = pd.to_datetime(ts["ds"])
        self._last_date = ts["ds"].max()

        if len(ts) >= 24:
            self._fitted = self._fit_prophet(ts)

        if not self._fitted:
            self._fit_arima(ts)

        return self

    def _fit_prophet(self, ts: pd.DataFrame) -> bool:
        try:
            from prophet import Prophet  # type: ignore

            m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            m.fit(ts)
            self._model = m
            self._model_name = "prophet"
            logger.info("Prophet fit succeeded.")
            return True
        except Exception as exc:
            logger.warning("Prophet fit failed (%s); falling back to ARIMA.", exc)
            return False

    def _fit_arima(self, ts: pd.DataFrame) -> None:
        from statsmodels.tsa.arima.model import ARIMA  # type: ignore

        self._arima_ts = ts
        # ARIMA(1,1,1) needs at least 4 points; fall back to linear for sparser data
        if len(ts) < 4:
            self._model = None
            self._model_name = "linear"
            self._linear_ts = ts
            self._fitted = True
            logger.info("Linear extrapolation used (very sparse data: %d rows).", len(ts))
            return

        m = ARIMA(ts["y"].values, order=(1, 1, 1))
        self._model = m.fit()
        self._model_name = "arima"
        logger.info("ARIMA fit used (sparse data: %d rows).", len(ts))
        self._fitted = True

    def predict(self, periods: int = 60) -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("Call fit() before predict().")

        if self._model_name == "prophet":
            future = self._model.make_future_dataframe(periods=periods, freq=self._freq)
            fc = self._model.predict(future)
            result = fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods).copy()
        elif self._model_name == "linear":
            ts = self._linear_ts
            last = self._last_date or pd.Timestamp("today")
            dates = pd.date_range(start=last, periods=periods + 1, freq=self._freq)[1:]
            # Fit a simple slope from available points; use last value if only 1 point
            if len(ts) >= 2:
                slope = float(np.polyfit(range(len(ts)), ts["y"].values, 1)[0])
                slope = max(slope, 0)  # no negative growth extrapolation
            else:
                slope = 0.0
            last_val = float(ts["y"].iloc[-1])
            yhat = np.array([last_val + slope * (i + 1) for i in range(periods)])
            margin = last_val * 0.3 + 1  # 30% confidence band
            result = pd.DataFrame({
                "ds": dates,
                "yhat": yhat,
                "yhat_lower": np.maximum(yhat - margin, 0),
                "yhat_upper": yhat + margin,
            })
        else:
            fc = self._model.get_forecast(steps=periods)
            ci = fc.conf_int()
            ci_lower = ci.iloc[:, 0].values if hasattr(ci, "iloc") else ci[:, 0]
            ci_upper = ci.iloc[:, 1].values if hasattr(ci, "iloc") else ci[:, 1]
            last = self._last_date or pd.Timestamp("today")
            dates = pd.date_range(start=last, periods=periods + 1, freq=self._freq)[1:]
            result = pd.DataFrame({
                "ds": dates,
                "yhat": fc.predicted_mean,
                "yhat_lower": ci_lower,
                "yhat_upper": ci_upper,
            })

        result["model_used"] = self._model_name
        result = result.reset_index(drop=True)
        return result

    def get_confidence_bands(self) -> pd.DataFrame:
        return self.predict(periods=60)[["ds", "yhat_lower", "yhat_upper", "model_used"]]


def load_registration_timeseries(parquet_path: str = PARQUET_PATH) -> pd.DataFrame:
    """
    Derives a monthly time-series from the raw EV population snapshot.
    The dataset only has Model Year (not a true date), so we synthesise a
    year-end date per county per model year as the best proxy.
    """
    import duckdb

    query = f"""
        SELECT
            County                     AS county,
            CAST("Model Year" AS INT)  AS year,
            COUNT(*)                   AS registrations
        FROM '{parquet_path}'
        WHERE "Model Year" IS NOT NULL
          AND CAST("Model Year" AS INT) < 2024
          AND State = 'WA'
        GROUP BY county, year
        ORDER BY county, year
    """
    df = duckdb.query(query).to_df()
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-12-31")
    return df[["county", "date", "registrations"]]
