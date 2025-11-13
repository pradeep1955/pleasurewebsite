# In mystocks/utils.py

import yfinance as yf
from django.utils import timezone
from datetime import timedelta
from .models import StockPrice
import logging # Import the logging module
import pandas as pd
logger = logging.getLogger(__name__) # Get a logger for this module

def fetch_and_store_if_needed(symbol):
    """
    Fetches and stores stock data only if the existing data is stale or missing.
    Corrected version without the invalid YFinanceRateLimitError exception.
    """
    should_fetch = False
    latest_stock = None

    try:
        latest_stock = StockPrice.objects.filter(symbol=symbol).latest('last_updated')
        today_date = timezone.now().date()
        if latest_stock.last_updated.date() < today_date:
#        if timezone.now() - latest_stock.last_updated > timedelta(minutes=15):
            logger.debug(f"Data for {symbol} is from a previous day ({latest_stock.last_updated.date()}). Fetching new data for {today_date}.")
#            logger.debug(f"Data for {symbol} is stale. Fetching new data.")
            should_fetch = True
        else:
            logger.debug(f"Data for {symbol} is up-to-date for today ({latest_stock.last_updated.date()}).Using cached data from DB.")
#            logger.debug(f"Data for {symbol} is fresh. Using cached data from DB.")
            return latest_stock # Return fresh data

    except StockPrice.DoesNotExist:
        logger.debug(f"No data for {symbol} found. Fetching initial data.")
        should_fetch = True

    if should_fetch:
        try:
            logger.debug(f"--- Attempting to fetch data for {symbol} from yfinance ---")
            stock = yf.Ticker(symbol)
            data = stock.history(period='6mo', interval='1d') # Consider a shorter period if needed

            if data.empty:
                logger.warning(f"!!! yfinance returned no data for {symbol}. Returning old data if available. !!!")
                return latest_stock # Return old data if fetch fails

            StockPrice.objects.filter(symbol=symbol).delete()

            prices_to_create = []
            for index, row in data.iterrows():
                # Add validation for NaN values which can cause DB errors
                if any(pd.isna(row[col]) for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                   logger.warning(f"Skipping row for {symbol} on {index.date()} due to NaN values.")
                   continue
                   
                prices_to_create.append(
                    StockPrice(
                        symbol=symbol,
                        date=index.date(),
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=row['Volume'],
                        last_updated=timezone.now()
                    )
                )

            if prices_to_create: # Only run bulk_create if there's valid data
                StockPrice.objects.bulk_create(prices_to_create)
                logger.debug(f"--- Successfully fetched and stored new data for {symbol} ---")
                latest_stock = StockPrice.objects.filter(symbol=symbol).latest('date')
                return latest_stock # Return newly fetched data
            else:
                logger.warning(f"No valid price data found for {symbol} after filtering NaNs. Returning old data.")
                return latest_stock # Return old data if all new rows were invalid

        # REMOVED the specific except yf.exceptions.YFinanceRateLimitError block

        except Exception as e:
            # Catch any other potential errors during the fetch
            logger.error(f"!!! An unexpected error occurred fetching {symbol}: {e} !!!", exc_info=True) # Log full traceback
            return latest_stock # Return old data on error

    # Fallback return
    return latest_stock
