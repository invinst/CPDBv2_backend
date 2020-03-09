from mock import patch

from django.test.testcases import TestCase
from django.conf import settings
from robber import expect

from analytics.utils.clicky_tracking import clicky_tracking
from analytics.constants import CLICKY_API_END_POINT


class ClickyTrackingTestCase(TestCase):
    @patch('requests.get')
    def test_clicky_tracking(self, mocked_get):
        request_data = {
            'type': 'event',
            'href': '/search',
            'title': 'Search',
            'ip_address': '192.168.3.3',
            'user_agent': 'Opera 19'
        }
        expected_clicky_request_data = {
            'site_id': settings.CLICKY_TRACKING_ID,
            'sitekey_admin': settings.CLICKY_SITEKEY_ADMIN,
            'type': 'event',
            'href': '/search',
            'title': 'Search',
            'ip_address': '192.168.3.3',
            'ua': 'Opera 19',
        }
        clicky_tracking(request_data)
        expect(mocked_get).to.be.called_with(CLICKY_API_END_POINT, params=expected_clicky_request_data)

    @patch('requests.get')
    def test_clicky_tracking_with_some_empty_fields(self, mocked_get):
        request_data = {
            'type': 'event',
            'href': '/search',
            'ip_address': '192.168.3.3',
            'user_agent': 'Opera 19'
        }
        expected_clicky_request_data = {
            'site_id': settings.CLICKY_TRACKING_ID,
            'sitekey_admin': settings.CLICKY_SITEKEY_ADMIN,
            'type': 'event',
            'href': '/search',
            'title': None,
            'ip_address': '192.168.3.3',
            'ua': 'Opera 19',
        }
        clicky_tracking(request_data)
        expect(mocked_get).to.be.called_with(CLICKY_API_END_POINT, params=expected_clicky_request_data)
