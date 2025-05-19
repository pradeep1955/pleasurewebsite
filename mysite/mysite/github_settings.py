#56705d89d857e0189227cca64c3ab1b3f36926a6
# Copy this file to github_settings.py (don't check it into github)

# Go to https://github.com/settings/developers

# Add a New OAuth2 App 

# Using PythonAnywhere here are some settings:

# Application name: ChuckList PythonAnywhere
# Homepage Url: https://drchuck.pythonanywhere.com
# Application Description: Whatever
# Authorization callback URL: https://drchuck.pythonanywhere.com/oauth/complete/github/

# Also on PythonAnywhere, go into the Web tab and enable "Force HTTPS"
# so you don't get a redirect URI mismatch.

# Then copy the client_key and secret to this file

#SOCIAL_AUTH_GITHUB_KEY = '69b1c9c208ddb599cbef'
SOCIAL_AUTH_GITHUB_KEY = 'Ov23lig6pIpjkOLAAmCu'
SOCIAL_AUTH_GITHUB_SECRET = '3eeb4d07e49ac2ee2fdee12e7704f5f80b07d4ef'

# Ask for the user's email (don't edit this line)
SOCIAL_AUTH_GITHUB_SCOPE = ['prdpchowdhary@gmail.com']

# Note you may not get email for github users that don't make their
# email public - that is OK

# For detail: https://python-social-auth.readthedocs.io/en/latest/configuration/django.html

# Using ngrok is hard because the url changes every time you start ngrok

# If you are running on localhost, here are some settings:

# Application name: ChuckList Local
# Homepage Url: http://localhost:8000
# Application Description: Whatever
# Authorization callback URL: http://127.0.0.1:8000/oauth/complete/github/


