from mock import patch

from django.test.testcases import TestCase
from django.conf import settings
from robber import expect

from analytics.utils.ga_tracking import ga_tracking
from analytics.constants import GA_API_END_POINT, GA_API_VERSION, GA_ANONYMOUS_ID


class GATrackingTestCase(TestCase):
    @patch('requests.post')
    def test_ga_tracking(self, mocked_post):
        request_data = {
            'hit_type': 'event',
            'event_category': 'outbound',
            'event_action': 'click',
            'event_label': '/document1',
            'event_value': 3,
            'page': '/officer/123/',
            'ip_address': '192.168.3.3',
            'user_agent': 'Opera 19'
        }
        expected_ga_request_data = {
            'v': GA_API_VERSION,
            'tid': settings.GA_TRACKING_ID,
            'cid': GA_ANONYMOUS_ID,
            't': 'event',
            'ec': 'outbound',
            'ea': 'click',
            'el': '/document1',
            'ev': 3,
            'dp': '/officer/123/',
            'uip': '192.168.3.3',
            'ua': 'Opera 19'
        }
        ga_tracking(request_data)
        expect(mocked_post).to.be.called_with(GA_API_END_POINT, data=expected_ga_request_data)

    @patch('requests.post')
    def test_ga_tracking_with_some_empty_fields(self, mocked_post):
        request_data = {
            'hit_type': 'event',
            'event_category': 'outbound',
            'event_action': 'click',
            'event_label': '/document1',
            'ip_address': '192.168.3.3',
            'user_agent': 'Opera 19'
        }
        expected_ga_request_data = {
            'v': GA_API_VERSION,
            'tid': settings.GA_TRACKING_ID,
            'cid': GA_ANONYMOUS_ID,
            't': 'event',
            'ec': 'outbound',
            'ea': 'click',
            'el': '/document1',
            'ev': None,
            'dp': None,
            'uip': '192.168.3.3',
            'ua': 'Opera 19'
        }
        ga_tracking(request_data)
        expect(mocked_post).to.be.called_with(GA_API_END_POINT, data=expected_ga_request_data)
