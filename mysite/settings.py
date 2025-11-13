import os
##import environ # Add this import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Initialize django-environ
##env = environ.Env()
##environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

from dotenv import load_dotenv
##import os
##BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))  # Add this line

#OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'default-api-key-if-missing')
#OPENAI_API_KEY=env('OPENAI_API_KEY')



OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'default-api-key-if-missing')
#api_key = os.getenv("OPENAI_API_KEY")


#load_dotenv()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Used for a default title
APP_NAME = 'Pleasure Web Site'   # Add

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
#SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# your_project/settings.py

# ... all your other settings like DEBUG = False ...

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    # This handler writes logs to the standard error stream
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    # Apply the handler to the loggers
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "home": {
            "handlers": ["console"],
            "level": "DEBUG", # Capture DEBUG messages from your 'home' app
            "propagate": True,
        },
        "news": {
            "handlers": ["console"],
            "level": "DEBUG", # Capture DEBUG messages from your 'news' app
            "propagate": True,
        },
    },
}


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Extensions - installed with pip3 / requirements.txt
    'django_extensions',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'social_django',
    'taggit',
    'home.apps.HomeConfig',
    'ads',
    'blog',
    'polls',
    'livestream',
    'myapp',
    'users',
    'event',
    'mystocks',
    'iotdata',
    'news',
    'shop',
    'portfolio',
    'myebike',
    # Sample Applications - don't copy
]

#AUTH_USER_MODEL = 'myapp.CustomUser'


# When we get to crispy forms :)
CRISPY_TEMPLATE_PACK = 'bootstrap5'  # Add

# When we get to tagging
TAGGIT_CASE_INSENSITIVE = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',   # Add
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'home/templates'), os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.settings',      # Add
                'social_django.context_processors.backends',  # Add
                'social_django.context_processors.login_redirect', # Add
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 'django.db.backends.sqlite3',
        'NAME': 'prdp1955$ads', # os.path.join(BASE_DIR, 'db.sqlite3'),
        'USER': 'prdp1955',
        'PASSWORD': 'deepa_1959',
        'HOST': 'PRDP1955.mysql.pythonanywhere-services.com',
        'OPTIONS': {
                  'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                   },
        'CONN_MAX_AGE': 60,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Add the settings below

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# Configure the social login
try:
    from . import github_settings
    SOCIAL_AUTH_GITHUB_KEY = github_settings.SOCIAL_AUTH_GITHUB_KEY
    SOCIAL_AUTH_GITHUB_SECRET = github_settings.SOCIAL_AUTH_GITHUB_SECRET
except:
    print('When you want to use social login, please see dj4e-samples/github_settings-dist.py')

# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html#authentication-backends
# https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html
AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    # 'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Don't set default LOGIN_URL - let django.contrib.auth set it when it is loaded
# LOGIN_URL = '/accounts/login'

# Needed for 3.2 and later
# https://stackoverflow.com/questions/67783120/warning-auto-created-primary-key-used-when-not-defining-a-primary-key-type-by
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# https://coderwall.com/p/uzhyca/quickly-setup-sql-query-logging-django
# https://stackoverflow.com/questions/12027545/determine-if-django-is-running-under-the-development-server

'''  # Leave off for now
import sys
if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
    print('Running locally')
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }
### auth password reset pw: "lkmt utfs nqwd oyhx "
'''

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
#EMAIL_HOST_USER =env('EMAIL_USER')

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
#EMAIL_HOST_PASSWORD = env('EMAIL_PASS')
MIDDLEWARE.insert(0, 'myapp.middleware.BlockBotMiddleware')


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME='pleasurewebsite-media'
#AWS_S3_SIGNATURE_NAME=''
AWS_S3_REGION_NAME='ap-south-1'
#AWS_S3_FILE_OVERWRITE=False
#AWS_S3_VERIFY=True
DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#AWS_DEFAULT_ACL = 'public-read' # Makes uploaded files publicly readable
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
