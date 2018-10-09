from __future__ import absolute_import, unicode_literals

from datetime import timedelta

import environ


ROOT_DIR = environ.Path(__file__) - 4  # (/root/cpdb/config/settings/myfile.py - 4 = /)
APPS_DIR = ROOT_DIR.path('cpdb')

env = environ.Env()
environ.Env.read_env("{root}/.env".format(root=ROOT_DIR))  # reading .env file

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'django_nose',
    'taggit',
    'anymail',
    'corsheaders',
    'adminsortable'
)

LOCAL_APPS = (
    'data',
    'data_versioning',
    'search',
    'vftg',
    'cms',
    'es_index',
    'analytics',
    'officers',
    'cr',
    'units',
    'alias',
    'twitterbot',
    'visual_token',
    'activity_grid',
    'document_cloud',
    'search_terms',
    'heatmap',
    'trr',
    'popup',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'twitterbot.middleware.LogTwitterbotLinkVisitMiddleware'
]

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', False)

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('CPDB', 'cpdb@eastagile.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': env.str('DB_HOST'),
        'NAME': env.str('DB_NAME'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'PORT': 5432,
        'USER': env.str('DB_USER')
    }
}

ROOT_URLCONF = 'config.urls'

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates'))
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'config.loaders.AzureStorageLoader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(APPS_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# REST FRAMEWORK SETTINGS

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'ORDERING_PARAM': 'sort'
}

MAILCHIMP_API_KEY = env.str('MAILCHIMP_API_KEY', default='')
MAILCHIMP_USER = env.str('MAILCHIMP_USER', default='')
VFTG_LIST_ID = 'e38095f8d7'

AZURE_STORAGE_ACCOUNT_NAME = env.str('AZURE_STORAGE_ACCOUNT_NAME', default='')
AZURE_STORAGE_ACCOUNT_KEY = env.str('AZURE_STORAGE_ACCOUNT_KEY', default='')
TWITTERBOT_STORAGE_ACCOUNT_NAME = env.str('TWITTERBOT_STORAGE_ACCOUNT_NAME', default='')
TWITTERBOT_STORAGE_ACCOUNT_KEY = env.str('TWITTERBOT_STORAGE_ACCOUNT_KEY', default='')
AZURE_QUEUE_NAME = 'cpdpbot'
DATA_PIPELINE_STORAGE_ACCOUNT_NAME = env.str('DATA_PIPELINE_STORAGE_ACCOUNT_NAME', default='')
DATA_PIPELINE_STORAGE_ACCOUNT_KEY = env.str('DATA_PIPELINE_STORAGE_ACCOUNT_KEY', default='')
TWITTER_CONSUMER_KEY = env.str('TWITTER_CONSUMER_KEY', default='')
TWITTER_CONSUMER_SECRET = env.str('TWITTER_CONSUMER_SECRET', default='')
TWITTER_APP_TOKEN_KEY = env.str('TWITTER_APP_TOKEN_KEY', default='')
TWITTER_APP_TOKEN_SECRET = env.str('TWITTER_APP_TOKEN_SECRET', default='')

V1_URL = 'https://data.cpdp.co'

ELASTICSEARCH_HOSTS = ['localhost:9200']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'error-file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/pyenv/versions/cpdb/logs/django-error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'twitterbot-log': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/pyenv/versions/cpdb/logs/twitterbot-webhook.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['error-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.command': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'twitterbot': {
            'handlers': ['twitterbot-log'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

TEST = False

VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER = str(APPS_DIR.path('visual_token_media'))
VISUAL_TOKEN_STORAGEACCOUNTNAME = env.str('VISUAL_TOKEN_STORAGEACCOUNTNAME', default='cpdbdev')
VISUAL_TOKEN_STORAGEACCOUNTKEY = env.str('VISUAL_TOKEN_STORAGEACCOUNTKEY', default='')

RUNNING_PORT = '80'

DOCUMENTCLOUD_USER = env.str('DOCUMENTCLOUD_USER', '')
DOCUMENTCLOUD_PASSWORD = env.str('DOCUMENTCLOUD_PASSWORD', '')

GOOGLE_GEOCODE_APIKEY = env.str('GOOGLE_GEOCODE_APIKEY', '')

ALLEGATION_MIN = env.str('ALLEGATION_MIN', '1988-01-01')
ALLEGATION_MAX = env.str('ALLEGATION_MAX', '2016-07-01')
INTERNAL_CIVILIAN_ALLEGATION_MIN = env.str('INTERNAL_CIVILIAN_ALLEGATION_MIN', '2000-01-01')
INTERNAL_CIVILIAN_ALLEGATION_MAX = env.str('INTERNAL_CIVILIAN_ALLEGATION_MIN', '2016-07-01')
TRR_MIN = env.str('TRR_MIN', '2004-01-08')
TRR_MAX = env.str('TRR_MAX', '2016-04-12')

AZURE_STATICFILES_CONTAINER = 'static'
AZURE_STATICFILES_SSL = False

TEMPLATE_TIME_TO_LIVE = timedelta(minutes=5)
AZURE_TEMPLATE_CONTAINER = 'templates'
