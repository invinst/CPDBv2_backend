from datetime import datetime

from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from officers.serializers import TimelineSerializer


class TimelineSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock()
        obj.to_dict = Mock(return_value={
            'a': 'b',
            'c': 'd',
            'date_sort': datetime.now(),
            'year_sort': 2000,
            'officer_id': 123
        })
        expect(TimelineSerializer(obj).data).to.eq({
            'a': 'b',
            'c': 'd'
        })

    def test_serialize_multiple(self):
        obj1 = Mock()
        obj1.to_dict = Mock(return_value={
            'a': 'b',
            'date_sort': datetime.now(),
            'year_sort': 2000,
            'officer_id': 123
        })
        obj2 = Mock()
        obj2.to_dict = Mock(return_value={
            'c': 'd',
            'date_sort': datetime.now(),
            'year_sort': 2000,
            'officer_id': 456
        })
        expect(TimelineSerializer([
            obj1, obj2
        ], many=True).data).to.eq([
            {'a': 'b'},
            {'c': 'd'}
        ])
