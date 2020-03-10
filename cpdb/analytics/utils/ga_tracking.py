import requests

from django.conf import settings

from analytics.constants import GA_ANONYMOUS_ID, GA_API_END_POINT, GA_API_VERSION


def ga_tracking(data):
    tracking_data = {
        'v': GA_API_VERSION,  # API Version.
        'tid': settings.GA_TRACKING_ID,  # Tracking ID / Property ID.
        # Anonymous Client Identifier. Ideally, this should be a UUID that
        # is associated with particular user, device, or browser instance.
        'cid': GA_ANONYMOUS_ID,
        't': data.get('hit_type'),  # Event hit type.
        'ec': data.get('event_category'),  # Event category.
        'ea': data.get('event_action'),  # Event action.
        'el': data.get('event_label'),  # Event label.
        'ev': data.get('event_value'),  # Event value, must be an integer.
        'dp': data.get('page'),  # Page
        'uip': data.get('ip_address'),  # IPaddress override.
        'ua': data.get('user_agent')  # Useragentoverride.
    }
    requests.post(GA_API_END_POINT, data=tracking_data)
