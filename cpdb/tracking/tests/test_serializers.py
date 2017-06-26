from django.test import TestCase

from freezegun import freeze_time
from robber import expect

from tracking.serializers import SearchTrackingSerializer
from tracking.factories import SearchTrackingFactory


class SearchTrackingSerializerTestCase(TestCase):
    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_serialize(self):
        search_tracking = SearchTrackingFactory(
            id=1, query='query', usages=1, results=1, query_type='free_text'
        )
        expect(SearchTrackingSerializer(search_tracking).data).to.be.eq({
            'id': 1,
            'query': 'query',
            'usages': 1,
            'results': 1,
            'query_type': 'free_text',
            'last_entered': '2017-01-14T12:00:01Z'
        })
