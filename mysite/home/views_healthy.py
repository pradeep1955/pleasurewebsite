from django.shortcuts import render
from django.views import View
from django.conf import settings
import requests
from django.http import JsonResponse
import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

# Set OpenAI API key
# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations
import logging
logger = logging.getLogger(__name__)

class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
       
        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': request.get_host().find('localhost') >= 0,
        }
        
        # Render the page with the news context
        return render(request, 'home/main.html', context)
    def get_completion(prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    def post(self, request):
        """
        Handle POST requests for the chatbot.
        """
        logger.info("POST request received.")
        logger.info(f"Message: {request.POST.get('message')}")
        user_message = request.POST.get('message')
        chatbot_response = "Sorry, something went wrong. Please try again."

        if user_message:
            try:
                # Set your OpenAI API key
                openai.api_key = settings.OPENAI_API_KEY  # Ensure OPENAI_API_KEY is set in your settings.py
            
                # Call OpenAI API
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Ensure you're using the correct model
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
            
                # Extract the AI's response
                chatbot_response = response['choices'][0]['message']['content']
        
            except Exception as e:
                logger.error(f"Chat bot error: {e}")
                chatbot_response = "Error: Unable to process the request. Please try again."
    
        # Return the chatbot response in JSON format
        return JsonResponse({'message': chatbot_response})
