# Create your views here.
# livestream/views.py
from django.shortcuts import render
from .models import LiveStream

def live_stream(request):
    # Fetch the first stream where 'is_live' is True
    stream = LiveStream.objects.filter(is_live=True).first()

    # Render the template and pass the stream object
    return render(request, 'livestream/live.html', {'stream': stream})
