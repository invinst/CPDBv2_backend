import json

from django.conf import settings

import requests
from requests.auth import HTTPBasicAuth


class MailchimpAPIError(Exception):
    def __init__(self, status_code, value):
        self.value = value
        self.status_code = status_code

    def __str__(self):
        return repr(self.value)


class MailchimpService:
    dc = settings.MAILCHIMP_API_KEY[-3:]
    list_member_url = f'https://{dc}.api.mailchimp.com/3.0/lists/{settings.VFTG_LIST_ID}/members/'

    @classmethod
    def subscribe(cls, email):
        response = requests.post(
            cls.list_member_url,
            data=json.dumps({'email_address': email, 'status': 'subscribed'}),
            auth=HTTPBasicAuth(settings.MAILCHIMP_USER, settings.MAILCHIMP_API_KEY))
        if response.status_code != 200:
            raise MailchimpAPIError(response.status_code, json.loads(response.content)['detail'])
