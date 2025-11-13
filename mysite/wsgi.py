"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

##import os


##from django.core.wsgi import get_wsgi_application

##os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

##application = get_wsgi_application()


import os
from dotenv import load_dotenv  # <-- Add this line

from django.core.wsgi import get_wsgi_application

# Define your project folder path
project_folder = '/home/prdp1955/django_projects/mysite'  # <-- replace with your actual path

# Load .env before Django loads settings
load_dotenv(os.path.join(project_folder, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
application = get_wsgi_application()


