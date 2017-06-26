from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
from freezegun import freeze_time

from tracking.factories import SearchTrackingFactory


class SearchTrackingViewTestCase(APITestCase):
    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_list_all_tracking(self):
        SearchTrackingFactory(id=1, query='query', usages=1, results=1, query_type='free_text')

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
            }]
        )
