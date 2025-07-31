# mystocks/views.py

import os
import io
import base64
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set backend for server-side rendering BEFORE importing pyplot
import matplotlib.pyplot as plt
import requests

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import StockPrice
from .utils import fetch_and_store_if_needed
from .gpt_commentary import generate_gpt_comment

# --- Main Chart View ---

@xframe_options_exempt
def stock_chart(request):
    """
    This view handles fetching stock data, generating a chart and commentary,
    and rendering it on the page. It includes caching logic to avoid
    hitting API rate limits.
    """
    # Get the stock symbol from the request, with a default value
    symbol = request.GET.get('symbol', 'SBIN.BO')
    favorite_stocks = ['SBIN.BO', 'TCS.BO', 'INFY.BO']
    
    # Ensure data is fresh (fetch if it's old or doesn't exist)
    fetch_and_store_if_needed(symbol)

    # Retrieve the latest data from the database
    data = StockPrice.objects.filter(symbol=symbol).order_by('date')

    chart = None
    comment = "No data available for this stock."

    if data.exists():
        # Convert the queryset to a Pandas DataFrame for analysis
        df = pd.DataFrame(list(data.values('date', 'close', 'volume')))
        df.set_index('date', inplace=True)

        # --- Technical Indicator Calculations ---
        # Moving Averages
        df['SMA50'] = df['close'].rolling(window=50).mean()
        df['SMA200'] = df['close'].rolling(window=200).mean()

        # MACD
        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # RSI Calculation
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        
        # Avoid division by zero for RSI
        rs = avg_gain / avg_loss.replace(0, 0.000001) # Replace 0 with a small number
        df['RSI'] = 100 - (100 / (1 + rs))

        # --- Generate AI Commentary ---
        # Get the latest data points for the commentary
        latest_rsi = df['RSI'].iloc[-1]
        latest_macd = df['MACD'].iloc[-1]
        latest_signal = df['Signal'].iloc[-1]
        comment = generate_gpt_comment(symbol, latest_rsi, latest_macd, latest_signal)

        # --- Plotting ---
        plt.style.use('dark_background')
        fig, axs = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
        fig.patch.set_facecolor('#121212')
        for ax in axs:
            ax.set_facecolor('#212121')
            ax.grid(True, linestyle='--', alpha=0.5)

        # Plot 1: Close price + SMA
        axs[0].plot(df.index, df['close'], label='Close Price', color='#00c8ff')
        axs[0].plot(df.index, df['SMA50'], label='SMA 50', color='#ffb347')
        axs[0].plot(df.index, df['SMA200'], label='SMA 200', color='#ff4040')
        axs[0].set_title(f'Price & Moving Averages for {symbol}')
        axs[0].legend()

        # Plot 2: Volume
        axs[1].bar(df.index, df['volume'], label='Volume', color='grey')
        axs[1].set_title('Trading Volume')
        axs[1].legend()

        # Plot 3: MACD
        axs[2].plot(df.index, df['MACD'], label='MACD', color='g')
        axs[2].plot(df.index, df['Signal'], label='Signal Line', color='r')
        axs[2].set_title('MACD')
        axs[2].legend()

        # Plot 4: RSI
        axs[3].plot(df.index, df['RSI'], label='RSI', color='purple')
        axs[3].axhline(70, color='red', linestyle='--')
        axs[3].axhline(30, color='green', linestyle='--')
        axs[3].set_title('Relative Strength Index (RSI)')
        axs[3].legend()

        plt.tight_layout()

        # Convert plot to a base64 image string to embed in HTML
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig) # Close the figure to free up memory

    # This is the context dictionary passed to the template
    context = {
        'chart': chart,
        'symbol': symbol,
        'favorite_stocks': favorite_stocks,
        'comment': comment
    }
    
    # This is the line that was causing the error (line 115 in your original file)
    # It is now correctly indented and will execute for all cases.
    return render(request, 'mystocks/stock_chart.html', context)


# --- API Views ---

@api_view(['POST'])
def stock_predict_api(request):
    """
    API endpoint to get GPT commentary for a stock based on technical indicators.
    """
    symbol = request.data.get('symbol')
    rsi = request.data.get('rsi')
    macd = request.data.gfet('macd')
    signal = request.data.get('signal')

    if not all([symbol, rsi, macd, signal]):
        return Response({'error': 'Missing required input data'}, status=400)
    
    try:
        comment = generate_gpt_comment(symbol, float(rsi), float(macd), float(signal))
        return Response({'comment': comment})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# --- Utility/Test View ---

def test_internet(request):
    """
    A simple view to test outbound internet connectivity, e.g., to the OpenAI API.
    """
    try:
        # Test connection to a reliable service
        response = requests.get("https://api.openai.com/v1", timeout=5)
        return HttpResponse(f"Successfully connected to OpenAI API. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Connection Error: {e}")
