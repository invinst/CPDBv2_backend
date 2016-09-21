from .common import *  # NOQA

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/pyenv/versions/cpdb/emails'
