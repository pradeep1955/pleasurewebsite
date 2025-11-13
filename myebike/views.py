import json
from django.shortcuts import render
from .models import GpsLog, Ride
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings # <-- NEW: To get your API key
import requests # <-- NEW: To call the Gemini API
from math import radians, sin, cos, sqrt, atan2 # For distance

# --- THIS IS YOUR SECRET KEY ---
MY_API_KEY = "api_key_12345" # <-- Make sure this is your key

# -----------------------------------------------------------------
#  HELPER FUNCTION: Haversine Formula (Unchanged)
# -----------------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# -----------------------------------------------------------------
#  API VIEW: /myebike/log_location/ (Unchanged)
# -----------------------------------------------------------------
@csrf_exempt
def log_location(request):
    # ... (This function is unchanged)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    key = request.headers.get('X-API-KEY')
    if key != MY_API_KEY:
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Invalid API Key'}, status=403)
    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lon = data.get('longitude')
        spd = data.get('speed', 0)
        ride_id = data.get('ride_id')
        if lat is None or lon is None or ride_id is None:
            return JsonResponse({'status': 'error', 'message': 'Missing latitude, longitude, or ride_id'}, status=400)
        try:
            ride_object = Ride.objects.get(id=ride_id)
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Ride with id {ride_id} does not exist.'}, status=404)
        GpsLog.objects.create(
            ride=ride_object, latitude=lat, longitude=lon, speed=spd
        )
        return JsonResponse({'status': 'success', 'message': 'Data logged to ride'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# -----------------------------------------------------------------
#  API VIEW: /myebike/api/start_new_ride/ (Unchanged)
# -----------------------------------------------------------------
@csrf_exempt
def start_new_ride(request):
    # ... (This function is unchanged)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    key = request.headers.get('X-API-KEY')
    if key != MY_API_KEY:
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Invalid API Key'}, status=403)
    ride_name = "Untitled Ride"
    try:
        if request.body:
            data = json.loads(request.body)
            ride_name = data.get('name', ride_name)
    except json.JSONDecodeError:
        pass 
    try:
        new_ride = Ride.objects.create(name=ride_name)
        return JsonResponse({
            'status': 'success', 'message': 'New ride created',
            'new_ride_id': new_ride.id, 'name': new_ride.name
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Could not create ride: {str(e)}'}, status=500)


# -----------------------------------------------------------------
#  HELPER FUNCTION: generate_plot_base64 (Unchanged)
# -----------------------------------------------------------------
def generate_plot_base64(lats, lons):
    # ... (This function is unchanged)
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1)
    if lats and lons:
        ax.plot(lons, lats, color='#00BFFF', marker='o', markersize=2, label='E-Bike Path')
        ax.set_title('E-Bike Ride Plot', color='white')
        ax.set_xlabel('Longitude', color='white')
        ax.set_ylabel('Latitude', color='white')
        ax.set_facecolor('#212529')
        fig.patch.set_facecolor('#343a40')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
    else:
        ax.text(0.5, 0.5, 'No Ride Data Available',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='white', fontstyle='italic')
        ax.set_facecolor('#212529')
        fig.patch.set_facecolor('#343a40')
        ax.tick_params(axis='x', colors='#555')
        ax.tick_params(axis='y', colors='#555')
        for spine in ax.spines.values():
            spine.set_edgecolor('#555')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getbuffer()).decode('utf-8')
    buf.close()
    return image_base64


# -----------------------------------------------------------------
#  NEW API VIEW: /api/generate_story/<int:ride_id>/
#  This calls the Gemini API!
# -----------------------------------------------------------------
def generate_ride_story(request, ride_id):
    try:
        # 1. Find the ride and calculate its stats
        ride = Ride.objects.get(id=ride_id)
        logs = ride.logs.all()
        
        total_distance = 0.0
        if logs.count() > 1:
            for i in range(logs.count() - 1):
                point_a = logs[i]
                point_b = logs[i+1]
                total_distance += haversine(
                    point_a.latitude, point_a.longitude,
                    point_b.latitude, point_b.longitude
                )
        
        avg_speed = 0.0
        if logs.count() > 0:
            total_speed = sum(log.speed for log in logs)
            avg_speed = total_speed / logs.count()

        # 2. Create a prompt for the Gemini API
        prompt = (
            "You are an enthusiastic e-bike rider and fitness blogger. "
            f"Write a short, exciting, and creative journal entry (about 2-3 sentences) "
            f"about a ride you just completed with the following stats:\n"
            f"Ride Name: {ride.name}\n"
            f"Distance: {round(total_distance, 1)} km\n"
            f"Average Speed: {round(avg_speed, 1)} km/h\n"
            "Make it sound fun and inspiring!"
        )

        # 3. Get the API Key from settings.py
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set in settings.py")
        except AttributeError:
            return JsonResponse({'error': 'GEMINI_API_KEY not found in settings.py'}, status=500)
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # 4. Call the Gemini API
        response = requests.post(
            api_url, 
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status() # Raise an error if the request failed
        
        result = response.json()
        story = result['candidates'][0]['content']['parts'][0]['text']
        
        # 5. Return the generated story
        return JsonResponse({'story': story})

    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'}, status=404)
    except Exception as e:
        # This will catch errors from the Gemini API (like quota)
        return JsonResponse({'error': str(e)}, status=500)


# -----------------------------------------------------------------
#  UPDATED VIEW: The "Home" Page
#  (Now sends ride.id, total_km, and avg_speed to the template)
# -----------------------------------------------------------------
def myebike_home(request):
    story = "This is the story of my awesome e-bike and its journeys..."
    all_rides = Ride.objects.order_by('-start_time')
    ride_data_list = []
    
    for ride in all_rides:
        logs = ride.logs.all().order_by('timestamp')
        lats = [log.latitude for log in logs]
        lons = [log.longitude for log in logs]
        
        plot_image_base64 = None
        if lats and lons:
            plot_image_base64 = generate_plot_base64(lats, lons)
        
        # Calculate stats for this ride
        total_distance = 0.0
        if logs.count() > 1:
            for i in range(logs.count() - 1):
                point_a = logs[i]
                point_b = logs[i+1]
                total_distance += haversine(
                    point_a.latitude, point_a.longitude,
                    point_b.latitude, point_b.longitude
                )
        
        avg_speed = 0.0
        if logs.count() > 0:
            total_speed = sum(log.speed for log in logs)
            avg_speed = total_speed / logs.count()

        ride_data_list.append({
            'id': ride.id, # <-- NEW: Send the ID
            'name': ride.name,
            'date': ride.start_time.strftime("%b %d, %Y"),
            'plot': plot_image_base64,
            'total_km': round(total_distance, 2),
            'avg_speed': round(avg_speed, 1) # <-- NEW: Send Avg Speed
        })

    context = {
        'story': story,
        'rides_json': json.dumps(ride_data_list, cls=DjangoJSONEncoder)
    }
    
    return render(request, 'myebike/home.html', context)
