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
from django.utils.decorators import method_decorator
import json
from .models import SensorReading
from django.utils.timezone import localtime
from django.utils import timezone
from datetime import timedelta


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

# Set OpenAI API key
# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations
import logging
logger = logging.getLogger(__name__)

sensor_data = {"temperature": None, "humidity": None}



@method_decorator(never_cache, name='dispatch')
class HomeView(View):
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


    def post(self, request):
        logger.info("POST request received.")
        user_message = request.POST.get('message')
        chatbot_response = "Sorry, something went wrong. Please try again."

        if user_message:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": user_message}]
                )
                chatbot_response = response['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"Chat bot error: {e}")
                chatbot_response = "Error: Unable to process the request. Please try again."

        return JsonResponse({'message': chatbot_response})



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
