from __future__ import absolute_import, unicode_literals

from datetime import timedelta

import environ


ROOT_DIR = environ.Path(__file__) - 4  # (/root/cpdb/config/settings/myfile.py - 4 = /)
APPS_DIR = ROOT_DIR.path('cpdb')

env = environ.Env()
environ.Env.read_env(f'{ROOT_DIR}/.env')  # reading .env file

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default='django')

ALLOWED_HOSTS = ['*']

SITE_ID = 1

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
    'django.contrib.sitemaps',
    'django.contrib.sites',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'django_nose',
    'taggit',
    'taggit_serializer',
    'anymail',
    'corsheaders',
    'adminsortable',
    'bandit',
    'sortedm2m'
)

LOCAL_APPS = (
    'data',
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
    'activity_grid',
    'document_cloud',
    'search_terms',
    'heatmap',
    'trr',
    'popup',
    'airtable_integration',
    'data_importer',
    'status',
    'email_service',
    'social_graph',
    'xlsx',
    'tracker',
    'sitemap',
    'activity_log',
    'pinboard',
    'toast',
    'app_config',
    'lawsuit',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'twitterbot.middleware.LogTwitterbotLinkVisitMiddleware',
    'config.cache.set_user_with_rest_framework_authenticator_middleware',
    'config.cache.FetchFromCacheForAnonymousUserMiddleware',
]

# CACHES CONFIGURATION
# ------------------------------------------------------------------------------
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'django'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


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
        'HOST': env.str('DB_HOST', 'postgres'),
        'NAME': env.str('DB_NAME', 'cpdb'),
        'PASSWORD': env.str('DB_PASSWORD', 'password'),
        'PORT': 5432,
        'USER': env.str('DB_USER', 'cpdb')
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
                'django.template.loaders.app_directories.Loader'
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
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
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

ELASTICSEARCH_HOSTS = ['elasticsearch:9200']

TEST = False

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

AIRTABLE_PROJECT_KEY = env.str('AIRTABLE_PROJECT_KEY', '')
AIRTABLE_TABLE_NAME = env.str('AIRTABLE_TABLE_NAME', 'Request a FOIA')

AIRTABLE_LAWSUITS_PROJECT_KEY = env.str('AIRTABLE_LAWSUITS_PROJECT_KEY', '')
AIRTABLE_LAWSUITS_TABLE_NAME = env.str('AIRTABLE_LAWSUITS_TABLE_NAME', 'Case')
AIRTABLE_PLAINTIFFS_TABLE_NAME = env.str('AIRTABLE_PLAINTIFFS_TABLE_NAME', 'Victims')
AIRTABLE_PAYMENTS_TABLE_NAME = env.str('AIRTABLE_PAYMENTS_TABLE_NAME', 'Payments')
AIRTABLE_LISTED_COPS_TABLE_NAME = env.str('AIRTABLE_LISTED_COPS_TABLE_NAME', 'Cops (we listed)')

AIRTABLE_COPA_AGENCY_ID = ''
AIRTABLE_CPD_AGENCY_ID = ''

TEMPLATE_TIME_TO_LIVE = timedelta(minutes=5)
AZURE_TEMPLATE_CONTAINER = 'templates'

S3_BUCKET_XLSX_DIRECTORY = 'xlsx'
S3_BUCKET_PDF_DIRECTORY = 'pdf'
S3_BUCKET_ZIP_DIRECTORY = 'zip'

GOOGLE_APPLICATION_CREDENTIALS = env.str('GOOGLE_APPLICATION_CREDENTIALS', default='')
GOOGLE_ANALYTICS_VIEW_ID = '129538462'

ENABLE_SITEMAP = False

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None

CPDP_ALERTS_WEBHOOK = env.str('CPDP_ALERTS_WEBHOOK', '')

ENABLE_MAKE_CLOUD_DOCUMENTS_PUBLIC = False
IMPORT_NOT_PUBLIC_CLOUD_DOCUMENTS = False

DOCUMENT_REQUEST_CC_EMAIL = 'documents@invisibleinstitute.com'

# If you want django-taggit to be CASE-INSENSITIVE when looking up existing tags,
# you’ll have to set the TAGGIT_CASE_INSENSITIVE setting to True (False by default)
# https://django-taggit.readthedocs.io/en/latest/getting_started.html
TAGGIT_CASE_INSENSITIVE = True

GA_TRACKING_ID = env.str('GA_TRACKING_ID', '')
CLICKY_TRACKING_ID = env.str('CLICKY_TRACKING_ID', '')
CLICKY_SITEKEY_ADMIN = env.str('CLICKY_SITEKEY_ADMIN', '')
