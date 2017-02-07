from django.test import SimpleTestCase

from robber import expect
from mock import patch

from analytics.serializers import EventSerializer


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
