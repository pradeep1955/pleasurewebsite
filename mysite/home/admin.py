from django.contrib import admin

# Register your models here.
from .models import SensorReading

admin.site.register(SensorReading)
