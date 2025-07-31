# mystocks/utils.py

import yfinance as yf
from django.utils import timezone
from datetime import timedelta
from .models import StockPrice

def fetch_and_store_if_needed(symbol):
    """
    Fetches and stores stock data only if the existing data is stale or missing.
    This function is now resilient to yfinance API errors.
    """
    should_fetch = False
    try:
        # Check if there is any existing data for the symbol
        latest_stock = StockPrice.objects.filter(symbol=symbol).latest('last_updated')
        
        # Check if the data is older than 15 minutes
        if timezone.now() - latest_stock.last_updated > timedelta(minutes=15):
            print(f"Data for {symbol} is stale. Fetching new data.")
            should_fetch = True
        else:
            print(f"Data for {symbol} is fresh. Using cached data from DB.")
            
    except StockPrice.DoesNotExist:
        # If no data exists at all, we definitely need to fetch it
        print(f"No data for {symbol} found. Fetching initial data.")
        should_fetch = True

    if should_fetch:
        try:
            print(f"--- Attempting to fetch data for {symbol} from yfinance ---")
            stock = yf.Ticker(symbol)
            # Fetch historical data for the last 6 months
            data = stock.history(period='6mo', interval='1d')

            if data.empty:
                print(f"yfinance returned no data for {symbol}.")
                return # Exit the function if no data is returned

            # Delete old records before inserting new ones
            StockPrice.objects.filter(symbol=symbol).delete()

            # Prepare data for bulk creation
            prices_to_create = []
            for index, row in data.iterrows():
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
            
            # Create all new records in a single database query
            StockPrice.objects.bulk_create(prices_to_create)
            print(f"--- Successfully fetched and stored new data for {symbol} ---")

        # --- THIS IS THE CRITICAL FIX ---
        # Catch the specific rate limit error and other potential yfinance issues
        except yf.exceptions.YFRateLimitError:
            print(f"!!! YFINANCE RATE LIMIT ERROR for {symbol}. Skipping fetch. The app will use old data. !!!")
            # We purposefully do nothing here, so the app doesn't crash.
            pass
        except Exception as e:
            # Catch any other potential errors during the fetch (e.g., network issues)
            print(f"!!! An unexpected error occurred while fetching data for {symbol}: {e} !!!")
            # Also pass here to prevent a crash
            pass
