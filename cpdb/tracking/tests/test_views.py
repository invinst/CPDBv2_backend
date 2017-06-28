from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
from freezegun import freeze_time

from tracking.factories import SearchTrackingFactory


class SearchTrackingViewTestCase(APITestCase):
    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
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
                'last_entered': '2017-01-14T12:00:01Z'
            }, {
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01Z'
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
                'last_entered': '2017-01-14T12:00:01Z'
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
                'last_entered': '2017-01-14T12:00:01Z'
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
                'last_entered': '2017-01-14T12:00:01Z'
            }, {
                'id': 1,
                'query': 'query',
                'usages': 1,
                'results': 1,
                'query_type': 'free_text',
                'last_entered': '2017-01-14T12:00:01Z'
            }]
        )

    def test_filter_by_query_type(self):
        url = reverse('api-v2:search-tracking-list')
        response = self.client.get(url, {'query_type': 'no_interaction'})
        expect(response.data['results']).to.eq(
            [{
                'id': 2,
                'query': 'qu',
                'usages': 2,
                'results': 2,
                'query_type': 'no_interaction',
                'last_entered': '2017-01-14T12:00:01Z'
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
                'last_entered': '2017-01-14T12:00:01Z'
            }]
        )
