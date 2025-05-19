import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import StockPrice
from .utils import fetch_and_store_if_needed
import matplotlib
matplotlib.use('Agg')  # Safe for server-side rendering
plt.style.use('dark_background')
from django.views.decorators.clickjacking import xframe_options_exempt
from .gpt_commentary import generate_gpt_comment

import os
print("Loaded API Key:", os.getenv("OPENAI_API_KEY"))


@xframe_options_exempt
def stock_chart(request):
    symbol = request.GET.get('symbol', 'SBIN.BO')  # Default to SBIN.BO
    favorite_stocks = ['SBIN.BO', 'BHARTIARTL.BO', 'TCS.BO', 'INFY.BO', 'ADANIPORTS.BO']
    # Delete old data before fetching fresh
    StockPrice.objects.filter(symbol=symbol).delete()
    fetch_and_store_if_needed(symbol)
    data = StockPrice.objects.filter(symbol=symbol).order_by('date')

   
    if not data.exists():
        chart = None
        comment = "No data available to generate commentary."
    else:
        df = pd.DataFrame(list(data.values('date', 'close', 'volume')))
        df.set_index('date', inplace=True)

        # (Calculations stay the same: SMA, MACD, RSI)

        # ... [Keep the same plotting code from previous step] ...


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
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))



        # Simple expert-like logic

        latest_rsi = df['RSI'].iloc[-1]
        latest_macd = df['MACD'].iloc[-1]
        latest_signal = df['Signal'].iloc[-1]

        comment = generate_gpt_comment(symbol, latest_rsi, latest_macd, latest_signal)

       # comment = generate_commentary(df)
        # Plot setup
        fig, axs = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
       # fig.patch.set_facecolor('#f8f9fa')  # Light grey background
        #for ax in axs:
        #    ax.grid(True, linestyle='--', alpha=0.5)
        #    ax.set_facecolor('#ffffff')  # White plot background

        fig.patch.set_facecolor('#121212')
        for ax in axs:
            ax.set_facecolor('#212121')


        # Plot 1: Close price + SMA
        axs[0].plot(df.index, df['close'], label='Close Price', color='#00c8ff')
        axs[0].plot(df.index, df['SMA50'], label='SMA 50', color='#ffb347')
        axs[0].plot(df.index, df['SMA200'], label='SMA 200', color='#ff4040')
        axs[0].set_title('Close Price & Moving Averages')
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

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()

    return render(request, 'mystocks/stock_chart.html', {
        'chart': chart,
        'symbol': symbol,
        'favorite_stocks': favorite_stocks, 
        'comment': comment
    })

import requests
from django.http import HttpResponse

def test_internet(request):
    try:
        response = requests.get("https://api.openai.com/v1")
        return HttpResponse(f"OpenAI API status: {response.status_code}")
    except Exception as e:
        return HttpResponse(f"Connection Error: {e}")

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .gpt_commentary import generate_gpt_comment

@api_view(['POST'])
def stock_predict_api(request):
    symbol = request.data.get('symbol')
    rsi = request.data.get('rsi')
    macd = request.data.get('macd')
    signal = request.data.get('signal')

    if not all([symbol, rsi, macd, signal]):
        return Response({'error': 'Missing input'}, status=400)

    try:
        comment = generate_gpt_comment(symbol, float(rsi), float(macd), float(signal))
        return Response({'comment': comment})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
