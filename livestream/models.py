# Create your models here.
# livestream/models.py
from django.db import models

class LiveStream(models.Model):
    title = models.CharField(max_length=100)  # Title of the stream
    is_live = models.BooleanField(default=False)  # Whether stream is live or not
    playback_url = models.URLField(blank=True, null=True)  # AWS IVS Playback URL

    def __str__(self):
        return self.title
