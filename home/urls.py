from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import HomeView, receive_sensor_data, chatbot_view

urlpatterns = [
    path('', views.HomeView.as_view(), name = 'home'),
    path('chat/', chatbot_view, name='chatbot'),
    path('sensor/', receive_sensor_data, name='sensor'),
]
