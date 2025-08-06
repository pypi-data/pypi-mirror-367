# core/cache/akshare_adapter.py
"""
AKShare adapter for the QuantDB core cache layer.

This module provides a unified interface for AKShare API calls,
with error handling and retry logic, but without direct cache integration.
"""

import re
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import akshare as ak
import pandas as pd
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from ..utils.logger import logger

class AKShareAdapter:
    """
    Adapter for AKShare API calls.

    This class provides methods for accessing AKShare data with
    error handling and retry logic, but without direct cache integration.
    """

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the AKShare adapter.

        Args:
            db: Database session (optional)
        """
        self.db = db
        logger.info("AKShare adapter initialized")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _safe_call(self, func: Any, *args, **kwargs) -> Any:
        """
        Safely call an AKShare function with retry logic.

        Args:
            func: The AKShare function to call.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result of the function call.

        Raises:
            Exception: If the function call fails after all retries.
        """
        try:
            # Log detailed call information
            arg_str = ', '.join([str(arg) for arg in args])
            kwarg_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
            logger.info(f"Calling AKShare function {func.__name__}({arg_str}, {kwarg_str})")

            # Execute function call
            result = func(*args, **kwargs)

            # Check if result is DataFrame and empty
            if isinstance(result, pd.DataFrame) and result.empty:
                logger.warning(f"AKShare function {func.__name__} returned empty DataFrame")
                logger.warning(f"Empty DataFrame returned for args={args}, kwargs={kwargs}")
            elif isinstance(result, pd.DataFrame):
                logger.info(f"AKShare function {func.__name__} returned DataFrame with {len(result)} rows")
                # Log date range information (if time series data)
                if 'date' in result.columns:
                    logger.info(f"Date range: {result['date'].min()} to {result['date'].max()}")

            return result
        except Exception as e:
            logger.error(f"Error calling AKShare function {func.__name__}: {e}")
            logger.error(f"Function arguments: args={args}, kwargs={kwargs}")
            # Log more detailed error information
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Log network-related error information
            if "ConnectionError" in str(e) or "Timeout" in str(e) or "HTTPError" in str(e):
                logger.error(f"Network-related error detected. This might be due to connectivity issues or API changes.")

            # Log possible API change information
            if "KeyError" in str(e) or "IndexError" in str(e) or "ValueError" in str(e):
                logger.error(f"Possible API change detected. The structure of the response may have changed.")

            raise

    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "",
        use_mock_data: bool = False,
        period: str = "daily"
    ) -> pd.DataFrame:
        """
        Get stock historical data.

        Args:
            symbol: Stock symbol.
            start_date: Start date in format YYYYMMDD.
            end_date: End date in format YYYYMMDD.
            adjust: Price adjustment method. Options are:
                   "" (empty string): No adjustment
                   "qfq": Forward adjustment
                   "hfq": Backward adjustment
            use_mock_data: If True, use mock data when AKShare returns empty data.
            period: Data frequency. Options are "daily", "weekly", "monthly".

        Returns:
            DataFrame with stock data.
        """
        logger.info(f"Getting stock data for {symbol} from {start_date} to {end_date} with adjust={adjust}, period={period}")

        # Validate parameters
        if not symbol:
            logger.error("Symbol cannot be empty")
            raise ValueError("Symbol cannot be empty")

        # Validate period parameter
        valid_periods = ["daily", "weekly", "monthly"]
        if period not in valid_periods:
            logger.error(f"Invalid period: {period}. Valid options are: {valid_periods}")
            raise ValueError(f"Invalid period: {period}. Valid options are: {valid_periods}")

        # Validate adjust parameter
        valid_adjusts = ["", "qfq", "hfq"]
        if adjust not in valid_adjusts:
            logger.error(f"Invalid adjust: {adjust}. Valid options are: {valid_adjusts}")
            raise ValueError(f"Invalid adjust: {adjust}. Valid options are: {valid_adjusts}")

        # Validate symbol format
        if not self._validate_symbol(symbol):
            logger.error(f"Invalid symbol format: {symbol}")
            if use_mock_data:
                logger.warning(f"Using mock data for invalid symbol: {symbol}")
                # Set default dates
                if end_date is None:
                    end_date = datetime.now().strftime('%Y%m%d')
                if start_date is None:
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                # Validate and format dates
                start_date = self._validate_and_format_date(start_date)
                end_date = self._validate_and_format_date(end_date)
                return self._generate_mock_stock_data(symbol, start_date, end_date, adjust, period)
            else:
                raise ValueError(f"Invalid symbol format: {symbol}. "
                               f"Symbol should be 6 digits for A-shares or 5 digits for Hong Kong stocks.")

        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            logger.info(f"No end date provided, using current date: {end_date}")

        if start_date is None:
            # Adjust default start date based on period
            if period == "daily":
                # Default to 1 year of daily data
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            elif period == "weekly":
                # Default to 2 years of weekly data
                start_date = (datetime.now() - timedelta(days=2*365)).strftime('%Y%m%d')
            else:  # monthly
                # Default to 5 years of monthly data
                start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y%m%d')
            logger.info(f"No start date provided, using default for {period} period: {start_date}")

        # Validate and format dates
        original_start_date = start_date
        original_end_date = end_date

        start_date = self._validate_and_format_date(start_date)
        end_date = self._validate_and_format_date(end_date)

        # Log date transformations for debugging
        if original_start_date != start_date:
            logger.info(f"Start date transformed from {original_start_date} to {start_date}")
        if original_end_date != end_date:
            logger.info(f"End date transformed from {original_end_date} to {end_date}")

        # Check if date range is valid
        if self._is_future_date(end_date):
            logger.warning(f"End date {end_date} is in the future. Setting to today.")
            end_date = datetime.now().strftime('%Y%m%d')

        if self._compare_dates(start_date, end_date) > 0:
            logger.error(f"Start date {start_date} is after end date {end_date}")
            raise ValueError(f"Start date {start_date} cannot be after end date {end_date}")

        # Detect market type and get data accordingly
        try:
            market = self._detect_market(symbol)
            logger.info(f"Detected market: {market} for symbol: {symbol}")

            # Standardize symbol for API call
            clean_symbol = symbol

            if market == 'A_STOCK':
                # Remove possible suffix
                if "." in clean_symbol:
                    clean_symbol = clean_symbol.split(".")[0]

                # Remove possible market prefix
                if clean_symbol.lower().startswith("sh") or clean_symbol.lower().startswith("sz"):
                    clean_symbol = clean_symbol[2:]

                logger.info(f"Getting A-share data using stock_zh_a_hist for {clean_symbol} with period={period}, adjust={adjust}")

                df = self._safe_call(
                    ak.stock_zh_a_hist,
                    symbol=clean_symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=adjust
                )

            elif market == 'HK_STOCK':
                # For Hong Kong stocks, use stock_hk_hist
                # Note: Hong Kong stock API might not support all adjust types
                logger.info(f"Getting Hong Kong stock data using stock_hk_hist for {clean_symbol} with period={period}")

                df = self._safe_call(
                    ak.stock_hk_hist,
                    symbol=clean_symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date
                    # Note: HK stocks might not support adjust parameter
                )

            else:
                raise ValueError(f"Unsupported market: {market}")

            if not df.empty:
                logger.info(f"Successfully retrieved {len(df)} rows of data for {symbol} ({market})")

                # Standardize column names
                df = self._standardize_stock_data(df)

                # Validate data integrity
                if self._validate_stock_data(df, symbol, start_date, end_date):
                    return df
                else:
                    logger.warning(f"Data validation failed for {symbol}. Will try alternative methods.")
            else:
                logger.warning(f"API returned empty data for {symbol} ({market})")

        except Exception as e:
            logger.error(f"Error getting data for {symbol}: {e}")

        # Check if the date range is in the future
        today = datetime.now().strftime('%Y%m%d')
        if self._compare_dates(start_date, today) > 0 and self._compare_dates(end_date, today) > 0:
            logger.warning(f"Date range {start_date} to {end_date} is entirely in the future. No data available.")
            # Return empty DataFrame for future dates
            return pd.DataFrame()

        # Check if we're requesting a single day that might be a non-trading day
        if start_date == end_date:
            # Check if it's a weekend
            date_obj = datetime.strptime(start_date, '%Y%m%d')
            if date_obj.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                logger.warning(f"Date {start_date} is a weekend (non-trading day). No data available.")
                return pd.DataFrame()

        # If all methods fail and mock data is allowed
        if use_mock_data:
            logger.warning(f"All data sources failed for {symbol}. Using mock data as requested.")
            return self._generate_mock_stock_data(symbol, start_date, end_date, adjust, period)

        # If all methods fail, return empty DataFrame
        logger.error(f"All methods failed to get data for {symbol}. Returning empty DataFrame.")
        return pd.DataFrame()

    def _validate_symbol(self, symbol: str) -> bool:
        """
        Validate stock symbol format - supports both A-shares and Hong Kong stocks.

        Args:
            symbol: Stock symbol to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not symbol or not symbol.isdigit():
            return False

        # Remove market prefix if present (for A-shares)
        if symbol.lower().startswith("sh") or symbol.lower().startswith("sz"):
            symbol = symbol[2:]

        # Remove suffix if present
        if "." in symbol:
            symbol = symbol.split(".")[0]

        # A-shares: 6-digit number (000001, 600000)
        if re.match(r'^\d{6}$', symbol):
            return True

        # Hong Kong stocks: 5-digit number (02171, 00700)
        if re.match(r'^\d{5}$', symbol):
            return True

        return False

    def _detect_market(self, symbol: str) -> str:
        """
        Detect which market the stock belongs to based on symbol format.

        Args:
            symbol: Stock symbol to analyze.

        Returns:
            Market identifier: 'A_STOCK' for A-shares, 'HK_STOCK' for Hong Kong stocks.

        Raises:
            ValueError: If symbol format is not supported.
        """
        # Clean symbol first
        clean_symbol = symbol

        # Remove market prefix if present (for A-shares)
        if clean_symbol.lower().startswith("sh") or clean_symbol.lower().startswith("sz"):
            clean_symbol = clean_symbol[2:]

        # Remove suffix if present
        if "." in clean_symbol:
            clean_symbol = clean_symbol.split(".")[0]

        if not clean_symbol.isdigit():
            raise ValueError(f"Invalid symbol format: {symbol}. Symbol must be numeric.")

        # A-shares: 6-digit number
        if len(clean_symbol) == 6:
            return 'A_STOCK'

        # Hong Kong stocks: 5-digit number
        elif len(clean_symbol) == 5:
            return 'HK_STOCK'

        else:
            raise ValueError(f"Unsupported symbol format: {symbol}. "
                           f"Expected 6 digits for A-shares or 5 digits for Hong Kong stocks.")

    def _validate_and_format_date(self, date_str: Optional[str]) -> str:
        """
        Validate and format date string.

        Args:
            date_str: Date string to validate and format.

        Returns:
            Formatted date string.
        """
        if date_str is None:
            return datetime.now().strftime('%Y%m%d')

        # Check if date is in YYYYMMDD format
        if not re.match(r'^\d{8}$', date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYYMMDD.")

        # Check if date is valid
        try:
            datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            raise ValueError(f"Invalid date: {date_str}")

        return date_str

    def _is_future_date(self, date_str: str) -> bool:
        """
        Check if date is in the future.

        Args:
            date_str: Date string in format YYYYMMDD.

        Returns:
            True if date is in the future, False otherwise.
        """
        date_obj = datetime.strptime(date_str, '%Y%m%d').date()
        return date_obj > datetime.now().date()

    def _compare_dates(self, date1: str, date2: str) -> int:
        """
        Compare two dates.

        Args:
            date1: First date in format YYYYMMDD.
            date2: Second date in format YYYYMMDD.

        Returns:
            -1 if date1 < date2, 0 if date1 == date2, 1 if date1 > date2.
        """
        date1_obj = datetime.strptime(date1, '%Y%m%d').date()
        date2_obj = datetime.strptime(date2, '%Y%m%d').date()

        if date1_obj < date2_obj:
            return -1
        elif date1_obj > date2_obj:
            return 1
        else:
            return 0

    def _standardize_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize stock data DataFrame.

        Args:
            df: DataFrame with stock data.

        Returns:
            Standardized DataFrame.
        """
        # Make a copy to avoid modifying the original
        result = df.copy()

        # Ensure date column is datetime
        if 'date' in result.columns or '日期' in result.columns:
            date_col = 'date' if 'date' in result.columns else '日期'
            result[date_col] = pd.to_datetime(result[date_col])
            if date_col != 'date':
                result.rename(columns={date_col: 'date'}, inplace=True)

        # Standardize column names
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'turnover',
            '振幅': 'amplitude',
            '涨跌幅': 'pct_change',
            '涨跌额': 'change',
            '换手率': 'turnover_rate'
        }

        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in result.columns:
                result.rename(columns={old_name: new_name}, inplace=True)

        return result

    def _validate_stock_data(self, df: pd.DataFrame, symbol: str, start_date: str, end_date: str) -> bool:
        """
        Validate stock data integrity.

        Args:
            df: DataFrame with stock data.
            symbol: Stock symbol.
            start_date: Start date in format YYYYMMDD.
            end_date: End date in format YYYYMMDD.

        Returns:
            True if data is valid, False otherwise.
        """
        if df.empty:
            logger.warning(f"Empty DataFrame for {symbol}")
            return False

        # Check required columns
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"Missing required column {col} for {symbol}")
                return False

        # Check date range
        if 'date' in df.columns:
            min_date = df['date'].min()
            max_date = df['date'].max()
            start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()

            # Allow some flexibility in date range
            # Data might not be available for weekends or holidays
            date_range_valid = (
                (min_date.date() - start_date_obj).days <= 7 and
                (end_date_obj - max_date.date()).days <= 7
            )

            if not date_range_valid:
                logger.warning(f"Date range mismatch for {symbol}. "
                              f"Requested: {start_date} to {end_date}, "
                              f"Got: {min_date.date()} to {max_date.date()}")
                return False

        return True

    def _generate_mock_stock_data(self, symbol: str, start_date: str, end_date: str, adjust: str, period: str) -> pd.DataFrame:
        """
        Generate mock stock data for testing purposes.

        Args:
            symbol: Stock symbol.
            start_date: Start date in format YYYYMMDD.
            end_date: End date in format YYYYMMDD.
            adjust: Price adjustment method.
            period: Data frequency.

        Returns:
            DataFrame with mock stock data.
        """
        logger.info(f"Generating mock data for {symbol} from {start_date} to {end_date}")

        # Create date range
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')

        # Generate business days only
        dates = pd.bdate_range(start=start_dt, end=end_dt, freq='B')

        if len(dates) == 0:
            return pd.DataFrame()

        # Generate mock price data
        import numpy as np
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed based on symbol

        base_price = 10.0 + (hash(symbol) % 100)  # Base price between 10-110
        prices = []
        current_price = base_price

        for i in range(len(dates)):
            # Random walk with slight upward bias
            change = np.random.normal(0.001, 0.02)  # 0.1% mean, 2% std
            current_price *= (1 + change)
            prices.append(current_price)

        # Create OHLC data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate OHLC around close price
            volatility = 0.02  # 2% intraday volatility
            high = close * (1 + np.random.uniform(0, volatility))
            low = close * (1 - np.random.uniform(0, volatility))
            open_price = low + (high - low) * np.random.uniform(0.2, 0.8)

            # Ensure OHLC relationships are valid
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            volume = int(np.random.uniform(1000000, 10000000))  # 1M-10M volume

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume,
                'turnover': round(close * volume, 2),
                'amplitude': round((high - low) / close * 100, 2),
                'pct_change': round((close - open_price) / open_price * 100, 2) if open_price > 0 else 0,
                'change': round(close - open_price, 2),
                'turnover_rate': round(np.random.uniform(0.5, 5.0), 2)
            })

        df = pd.DataFrame(data)
        logger.info(f"Generated {len(df)} rows of mock data for {symbol}")
        return df
