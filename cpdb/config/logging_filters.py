import logging

from django.conf import settings


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.environment = settings.ENVIRONMENT
        return True
