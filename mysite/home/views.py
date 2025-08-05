from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.conf import settings
import requests
from django.http import JsonResponse
import os
import logging
import openai
from django.views.decorators.csrf import csrf_exempt
from .models import SensorReading
import json
from django.views.generic import TemplateView
from django.utils.timezone import localtime
from django.utils import timezone
from datetime import timedelta

from news.models import DailyNews
from datetime import date
from news.utils import get_or_update_today_news
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

logger = logging.getLogger(__name__)

sensor_data = {"temperature": None, "humidity": None}



@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class HomeView(View):
    def get(self, request, *args, **kwargs):
        news = get_or_update_today_news()  # ✅ fetch today's news
        print("NEWS HTML:", news.summary_html)  # for debugging
        return render(request, 'home/main.html', {"news_summary": news.summary_html})

    def get(self, request):
        host = request.get_host()
        islocal = 'localhost' in host or '127.0.0.1' in host

        # Get last 12 hours of data
        now = timezone.now()
        start_time = now - timedelta(hours=12)
        readings = SensorReading.objects.filter(timestamp__gte=start_time).order_by('timestamp')

        # Downsample to 15-min intervals
        interval_readings = []
        last_time = None
        for reading in readings:
            if not last_time or (reading.timestamp - last_time).total_seconds() >= 900:
                interval_readings.append(reading)
                last_time = reading.timestamp

        # Get latest reading
        try:
            latest = SensorReading.objects.latest('timestamp')
        except SensorReading.DoesNotExist:
            latest = None

        context = {
            'temperature_data': [r.temperature for r in interval_readings],
            'humidity_data': [r.humidity for r in interval_readings],
            'labels': [localtime(r.timestamp).strftime("%H:%M") for r in interval_readings],
            'installed': settings.INSTALLED_APPS,
            'islocal': islocal,
            'temperature': latest.temperature if latest else None,
            'humidity': latest.humidity if latest else None,
            'last_updated': localtime(latest.timestamp).strftime("%Y-%m-%d %H:%M:%S") if latest else "No data",
        }
        return render(request, 'home/main.html', context)

@csrf_exempt
def receive_sensor_data(request):
    global sensor_data
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            temperature = data.get("temperature")
            humidity = data.get("humidity")
            sensor_data["temperature"] = temperature
            sensor_data["humidity"] = humidity

            SensorReading.objects.create(temperature=temperature, humidity=humidity)

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "only POST allowed"})


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            # Handling JSON POST request explicitly
            data = json.loads(request.body)
            user_message = data.get('message', "").strip()
            
            # Check for an empty message
            if not user_message:
                return JsonResponse({'message': "Please enter a valid message."})

            openai.api_key = settings.OPENAI_API_KEY

            # Calling OpenAI API to get the chatbot response
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Getting the response content
            chatbot_response = response.choices[0].message.content if response.choices[0] else "No response from model."

            return JsonResponse({'message': chatbot_response})
        
        except Exception as e:
            return JsonResponse({'message': "Error: Unable to process the request. Please try again. Detail: " + str(e)})
    
    else:
        return JsonResponse({"message": "This endpoint only accepts POST requests."})
