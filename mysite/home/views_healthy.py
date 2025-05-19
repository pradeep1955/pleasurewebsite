from django.shortcuts import render
from django.views import View
from django.conf import settings
import requests

# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations


class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
       


    def get(self, request):
        # Define the API endpoint and parameters
        api_url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'country': 'IN',  # India country code
            'category': 'general',  # General category
            'apiKey': '',  # Your API key
            'pageSize': 10  # Limit the number of headlines to 10
        }
        
        # Make the API request
        response = requests.get(api_url, params=params)
        
        print(f"API Status: {response.status_code}")
        print(f"API Response: {response.json()}")
        # Check if the request was successful
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
        else:
            articles = []  # Set to an empty list if there's an error
        
        # Pass the articles to the template
        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': request.get_host().find('localhost') >= 0,
            'india_news': articles  # Pass fetched articles to template
        }
        
        # Render the page with the news context
        return render(request, 'home/main.html', context)
