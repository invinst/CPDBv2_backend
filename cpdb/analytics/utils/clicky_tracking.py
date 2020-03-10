import requests
from django.conf import settings

from analytics.constants import CLICKY_API_END_POINT


def clicky_tracking(data):
    clicky_data = {
        'site_id': settings.CLICKY_TRACKING_ID,
        'sitekey_admin': settings.CLICKY_SITEKEY_ADMIN,
        'type': data.get('type', 'click'),
        'href': data.get('href'),
        'title': data.get('title'),
        'ip_address': data.get('ip_address'),
        'ua': data.get('user_agent'),
    }
    requests.get(CLICKY_API_END_POINT, params=clicky_data)
