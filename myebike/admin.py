from django.contrib import admin

# Register your models here.
# In myebike/admin.py
from .models import Ride, GpsLog

admin.site.register(Ride)
admin.site.register(GpsLog)
