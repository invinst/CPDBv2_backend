from django.test import SimpleTestCase, TestCase

from freezegun import freeze_time
from robber import expect
from mock import patch

from analytics.serializers import EventSerializer, SearchTrackingSerializer
from analytics.factories import SearchTrackingFactory


class EventSerializerTestCase(SimpleTestCase):
    def test_create(self):
        data = {
            'd': 'e',
        }
        serializer = EventSerializer(data={
            'name': 'abc',
            'data': data
        })
        expect(serializer.is_valid()).to.be.true()

        with patch('analytics.serializers.Event.objects.create') as mock_func:
            serializer.save()
            mock_func.assert_called_with(name='abc', data=data)


class SearchTrackingSerializerTestCase(TestCase):
    @freeze_time('2017-01-14 12:00:01-06:00')
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
            'last_entered': '2017-01-14T12:00:01-06:00'
        })
