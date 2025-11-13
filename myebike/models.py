# In myebike/models.py
from django.db import models

class Ride(models.Model):
    """
    Represents a single, complete ride.
    """
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ride {self.id}: {self.name}"

class GpsLog(models.Model):
    """
    Represents a single GPS point, linked to a Ride.
    """
    # This is the new, most important field!
    # It links this log entry to a Ride.
    # on_delete=models.CASCADE means if a Ride is deleted,
    # all its GPS points are deleted too.
    ride = models.ForeignKey(Ride, related_name='logs', on_delete=models.CASCADE, null=True, blank=True)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.ride.name} @ {self.timestamp.strftime('%H:%M')}"
