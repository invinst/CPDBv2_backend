from datetime import datetime
from mock import patch

from django.urls import reverse
from django.conf import settings

import pytz
from robber import expect
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from analytics.models import Event, AttachmentTracking
from analytics.factories import SearchTrackingFactory
from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import AllegationFactory, AttachmentFileFactory
from analytics.constants import CLICKY_API_END_POINT, GA_API_END_POINT, GA_API_VERSION, GA_ANONYMOUS_ID


class EventsViewTestCase(APITestCase):

    @freeze_time('2017-01-14 12:00:01')
    def test_created_at(self):
        data = {
            'id': 12,
            'title': 'How accurate is the data?'
        }

        url = reverse('api-v2:event-list')
        response = self.client.post(url, {
            'name': 'some-click',
            'data': data
        }, format='json')
        expect(response.status_code).to.eq(status.HTTP_201_CREATED)

        event = Event.objects.first()
        expect(event.name).to.eq('some-click')
        expect(event.data).to.eq(data)
        expect(event.created_at).to.eq(datetime(2017, 1, 14, 12, 0, 1, tzinfo=pytz.utc))


class SearchTrackingViewTestCase(APITestCase):
    @freeze_time('2017-01-14 12:00:01-06:00')
    def setUp(self):
        SearchTrackingFactory(id=1, query='query', usages=1, results=1, query_type='free_text')
        SearchTrackingFactory(id=2, query='qu', usages=2, results=2, query_type='no_interaction')

    def test_list_all_tracking(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url)

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data['results']).to.eq(
            [{
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }, {
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

    def test_pagination_tracking(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url, {
            'limit': 1,
            'offset': 0
        })

        expect(response.data['count']).to.eq(2)
        expect(response.data['results']).to.eq(
            [{
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

        response = self.client.get(url, {
            'limit': 1,
            'offset': 1
        })
        expect(response.data['count']).to.eq(2)
        expect(response.data['results']).to.eq(
            [{
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

    def test_ordering(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url, {'sort': '-usages'})
        expect(response.data['results']).to.eq(
            [{
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }, {
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

    def test_filter_by_query_type(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url, {'query_types': 'no_interaction'})
        expect(response.data['results']).to.eq(
            [{
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

        response = self.client.get(url, {'query_types': 'no_interaction,free_text'})
        expect(response.data['results']).to.eq(
            [{
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }, {
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )

    def test_search(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url, {'search': 'que'})
        expect(response.data['results']).to.eq(
            [{
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01-06:00'
            }]
        )


class AttachmentTrackingViewSetTestCase(APITestCase):
    def test_create_failure(self):
        response = self.client.post(reverse(
            'api-v2:attachment-tracking-list'),
            {'accessed_from_page': 'CR', 'app': 'frontend', 'attachment_id': 345}
        )

        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @freeze_time('2018-04-04 12:00:01', tz_offset=0)
    def test_create_success(self):
        allegation = AllegationFactory(crid=123456)
        attachment_file = AttachmentFileFactory(
            id=123,
            owner=allegation,
            title='CR document 10',
            tag='CR',
            url='https://cr-document.com/10',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url3',
        )

        expect(AttachmentTracking.objects.count()).to.eq(0)

        response = self.client.post(reverse(
            'api-v2:attachment-tracking-list'),
            {'accessed_from_page': 'CR', 'app': 'frontend', 'attachment_id': 123}
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(AttachmentTracking.objects.count()).to.eq(1)
        attachment_tracking = AttachmentTracking.objects.first()
        expect(attachment_tracking.created_at).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
        expect(attachment_tracking.attachment_file).to.eq(attachment_file)
        expect(attachment_tracking.accessed_from_page).to.eq('CR')
        expect(attachment_tracking.app).to.eq('frontend')


class TrackingViewSetTestCase(APITestCase):
    @patch('requests.post')
    @patch('requests.get')
    def test_create_tracking_fail(self, mocked_get, mocked_post):
        response = self.client.post(reverse(
            'api-v2:tracking-list'),
            {}
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(mocked_get).not_to.be.called()
        expect(mocked_post).not_to.be.called()

    @patch('requests.get')
    def test_create_clicky_tracking_success(self, mocked_get):
        self.client.credentials(REMOTE_ADDR='192.168.3.3', HTTP_USER_AGENT='Safari 19')
        clicky_tracking_data = {
            'type': 'click',
            'href': '/officer/123',
            'title': 'Officer Keith Herrera'
        }
        response = self.client.post(reverse(
            'api-v2:tracking-list'),
            {'clicky': clicky_tracking_data},
            format='json',
        )
        expected_clicky_tracking_data = {
            'type': 'click',
            'href': '/officer/123',
            'title': 'Officer Keith Herrera',
            'site_id': settings.CLICKY_TRACKING_ID,
            'sitekey_admin': settings.CLICKY_SITEKEY_ADMIN,
            'ip_address': '192.168.3.3',
            'ua': 'Safari 19'
        }
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(mocked_get).to.be.called_with(CLICKY_API_END_POINT, params=expected_clicky_tracking_data)

    @patch('requests.post')
    def test_create_ga_tracking_success(self, mocked_post):
        self.client.credentials(REMOTE_ADDR='192.168.3.3', HTTP_USER_AGENT='Safari 19')
        ga_tracking_data = {
            'hit_type': 'event',
            'event_category': 'outbound',
            'event_action': 'click',
            'event_label': '/document1',
            'event_value': 3,
        }
        response = self.client.post(reverse(
            'api-v2:tracking-list'),
            {'ga': ga_tracking_data},
            format='json',
        )
        expected_ga_tracking_data = {
            'v': GA_API_VERSION,
            'tid': settings.GA_TRACKING_ID,
            'cid': GA_ANONYMOUS_ID,
            't': 'event',
            'ec': 'outbound',
            'ea': 'click',
            'el': '/document1',
            'ev': 3,
            'dp': None,
            'uip': '192.168.3.3',
            'ua': 'Safari 19'
        }
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(mocked_post).to.be.called_with(GA_API_END_POINT, data=expected_ga_tracking_data)

    @patch('requests.post')
    @patch('requests.get')
    def test_create_tracking_success(self, mocked_get, mocked_post):
        self.client.credentials(REMOTE_ADDR='192.168.3.3', HTTP_USER_AGENT='Safari 19')
        ga_tracking_data = {
            'hit_type': 'event',
            'event_category': 'outbound',
            'event_action': 'click',
            'event_label': '/document1',
            'event_value': 3,
        }
        clicky_tracking_data = {
            'type': 'click',
            'href': '/officer/123',
            'title': 'Officer Keith Herrera'
        }
        response = self.client.post(reverse(
            'api-v2:tracking-list'),
            {'ga': ga_tracking_data, 'clicky': clicky_tracking_data},
            format='json',
        )
        expected_clicky_tracking_data = {
            'type': 'click',
            'href': '/officer/123',
            'title': 'Officer Keith Herrera',
            'site_id': settings.CLICKY_TRACKING_ID,
            'sitekey_admin': settings.CLICKY_SITEKEY_ADMIN,
            'ip_address': '192.168.3.3',
            'ua': 'Safari 19'
        }
        expected_ga_tracking_data = {
            'v': GA_API_VERSION,
            'tid': settings.GA_TRACKING_ID,
            'cid': GA_ANONYMOUS_ID,
            't': 'event',
            'ec': 'outbound',
            'ea': 'click',
            'el': '/document1',
            'ev': 3,
            'dp': None,
            'uip': '192.168.3.3',
            'ua': 'Safari 19'
        }
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(mocked_post).to.be.called_with(GA_API_END_POINT, data=expected_ga_tracking_data)
        expect(mocked_get).to.be.called_with(CLICKY_API_END_POINT, params=expected_clicky_tracking_data)
