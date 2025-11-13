# In myebike/urls.py
from django.urls import path
from . import views

app_name = 'myebike' # Good practice for namespacing

urlpatterns = [
    # 1. This is the "home" page for your app (e.g., .../myebike/)
    # It will run the `myebike_home` view
    path('', views.myebike_home, name='myebike_home'),
    
    # 2. This is the API endpoint you wanted (e.g., .../myebike/log_location/)
    # It will run the `log_location` view
    path('log_location/', views.log_location, name='log_location'),
    path('api/start_new_ride/', views.start_new_ride, name='start_new_ride'),
    path('api/generate_story/<int:ride_id>/', views.generate_ride_story, name='generate_ride_story'),
]

