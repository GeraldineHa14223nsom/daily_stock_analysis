"""Core stock analysis module for daily_stock_analysis.

Provides the StockAnalyzer class which fetches, processes, and summarizes
daily stock data using yfinance and basic technical indicators.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """Fetches and analyzes daily stock data for a given list of tickers."""

    def __init__(self, tickers: list[str], lookback_days: int = 30):
        """
        Initialize the analyzer.

        Args:
            tickers: List of stock ticker symbols (e.g. ['AAPL', 'MSFT']).
            lookback_days: Number of calendar days of history to fetch.
        """
        self.tickers = [t.upper().strip() for t in tickers if t.strip()]
        self.lookback_days = lookback_days
        self._data: dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def fetch(self) -> None:
        """Download OHLCV data for all tickers from Yahoo Finance."""
        end = datetime.today()
        start = end - timedelta(days=self.lookback_days)

        logger.info(
            "Fetching data for %d ticker(s) from %s to %s",
            len(self.tickers),
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
        )

        for ticker in self.tickers:
            try:
                df = yf.download(ticker, start=start, end=end, progress=False)
                if df.empty:
                    logger.warning("No data returned for ticker: %s", ticker)
                    continue
                df.index = pd.to_datetime(df.index)
                self._data[ticker] = df
                logger.debug("Fetched %d rows for %s", len(df), ticker)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to fetch %s: %s", ticker, exc)

    # ------------------------------------------------------------------
    # Technical indicators
    # ------------------------------------------------------------------

    @staticmethod
    def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Append SMA-5, SMA-20, and daily return columns to *df*."""
        df = df.copy()
        df["SMA_5"] = df["Close"].rolling(window=5).mean()
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["Daily_Return"] = df["Close"].pct_change() * 100
        return df

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(self) -> dict[str, dict]:
        """Run analysis on fetched data and return a summary dict.

        Returns:
            Mapping of ticker -> summary statistics.
        """
        if not self._data:
            logger.warning("No data available — call fetch() first.")
            return {}

        results: dict[str, dict] = {}

        for ticker, df in self._data.items():
            df = self._add_indicators(df)
            latest = df.iloc[-1]

            summary = {
                "date": df.index[-1].strftime("%Y-%m-%d"),
                "close": round(float(latest["Close"]), 4),
                "volume": int(latest["Volume"]),
                "daily_return_pct": round(float(latest["Daily_Return"]), 4),
                "sma_5": round(float(latest["SMA_5"]), 4) if pd.notna(latest["SMA_5"]) else None,
                "sma_20": round(float(latest["SMA_20"]), 4) if pd.notna(latest["SMA_20"]) else None,
                "trend": self._trend_signal(latest),
            }
            results[ticker] = summary
            logger.info("%s | %s", ticker, summary)

        return results

    @staticmethod
    def _trend_signal(row: pd.Series) -> Optional[str]:
        """Return a simple trend label based on SMA crossover."""
        sma5 = row.get("SMA_5")
        sma20 = row.get("SMA_20")
        if pd.isna(sma5) or pd.isna(sma20):
            return None
        if sma5 > sma20:
            return "bullish"
        if sma5 < sma20:
            return "bearish"
        return "neutral"
