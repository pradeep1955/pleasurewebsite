from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import HomeView, receive_sensor_data
urlpatterns = [
    path('', views.HomeView.as_view()),
    path('sensor/', receive_sensor_data, name='sensor'),
]
