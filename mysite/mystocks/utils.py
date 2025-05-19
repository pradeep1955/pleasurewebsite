import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from .models import StockPrice


def fetch_stock_data(symbol='SBIN.BO', period='1mo', interval='1d'):
    stock = yf.Ticker(symbol)
    return stock.history(period=period, interval=interval)


def plot_stock(data):
    plt.figure(figsize=(10,5))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title('Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    return image_base64

from .models import StockPrice

def save_stock_data(symbol='SBIN.BO', period='1mo', interval='1d'):
    data = fetch_stock_data(symbol, period, interval)
    for date, row in data.iterrows():
        StockPrice.objects.update_or_create(
            symbol=symbol,
            date=date.date(),
            defaults={
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            }
        )

from .models import StockPrice
import yfinance as yf

def fetch_and_store_if_needed(symbol):
    if not StockPrice.objects.filter(symbol=symbol).exists():
        stock = yf.Ticker(symbol)
        data = stock.history(period='6mo', interval='1d')

        for date, row in data.iterrows():
            StockPrice.objects.update_or_create(
                symbol=symbol,
                date=date.date(),
                defaults={
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': row['Volume']
                }
            )
