from datetime import datetime, date

from django.test import SimpleTestCase
from mock import Mock
from robber import expect

from officers.serializers import (
    TimelineSerializer, CRTimelineSerializer, TimelineMinimapSerializer, OfficerMetricsSerializer
)


class OfficerMetricsSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock(**{
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 2,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'discipline_count': 5,
            'civilian_compliment_count': 6,
            'first_name': 'Roberto',
            'last_name': 'Last Name',
            'race': 'Asian',
        })
        expect(OfficerMetricsSerializer(obj).data).to.eq({
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 2,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'discipline_count': 5,
            'civilian_compliment_count': 6
        })


class TimelineSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock()
        obj.to_dict = Mock(return_value={
            'a': 'b',
            'c': 'd',
            'date_sort': datetime.now(),
            'year_sort': 2000,
            'priority_sort': 40,
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
            'priority_sort': 40,
            'officer_id': 123
        })
        obj2 = Mock()
        obj2.to_dict = Mock(return_value={
            'c': 'd',
            'date_sort': datetime.now(),
            'year_sort': 2000,
            'priority_sort': 40,
            'officer_id': 456
        })
        expect(TimelineSerializer([
            obj1, obj2
        ], many=True).data).to.eq([
            {'a': 'b'},
            {'c': 'd'}
        ])


class CRTimelineSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock(**{
            'officer_id': 123,
            'start_date': date(2016, 1, 1),
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'XXX',
            'final_finding_display': 'Unfounded',
            'coaccused_count': 0,
            'allegation': Mock(**{
                'complainant_races': ['White'],
                'complainant_age_groups': ['31-40'],
                'complainant_genders': ['Female', 'Male']
            })
        })
        expect(CRTimelineSerializer(obj).data).to.eq({
            'officer_id': 123,
            'date': '2016-01-01',
            'date_sort': date(2016, 1, 1),
            'year_sort': 2016,
            'priority_sort': 40,
            'kind': 'CR',
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'XXX',
            'finding': 'Unfounded',
            'coaccused': 0,
            'race': ['White'],
            'age': ['31-40'],
            'gender': ['Female', 'Male']
        })

    def test_unknown_category(self):
        obj = Mock(**{
            'category': None,
            'subcategory': None,
            'officer_id': 123,
            'start_date': date(2016, 1, 1),
            'crid': '123456',
            'final_finding_display': 'Unfounded',
            'coaccused_count': 0,
            'allegation': Mock(**{
                'complainant_races': ['White'],
                'complainant_age_groups': ['31-40'],
                'complainant_genders': ['Female', 'Male']
            })
        })
        expect(CRTimelineSerializer(obj).data).to.eq({
            'category': 'Unknown',
            'subcategory': None,
            'officer_id': 123,
            'date': '2016-01-01',
            'date_sort': date(2016, 1, 1),
            'year_sort': 2016,
            'priority_sort': 40,
            'kind': 'CR',
            'crid': '123456',
            'finding': 'Unfounded',
            'coaccused': 0,
            'race': ['White'],
            'age': ['31-40'],
            'gender': ['Female', 'Male']
        })


class TimelineMinimapSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock(**{
            'x': 123,
            'date': '2017-05-01',
            'kind': 'CR',
        })
        expect(TimelineMinimapSerializer(obj).data).to.eq({
            'kind': 'CR',
            'year': 2017
        })

    def test_serialize_multiple(self):
        obj1 = Mock(**{
            'x': 123,
            'date': '2017-05-01',
            'kind': 'CR',
        })

        obj2 = Mock(**{
            'y': 321,
            'date': '2016-05-01',
            'kind': 'UNIT_CHANGE',
        })

        obj3 = Mock(**{
            'z': 333,
            'date': '2016-02-01',
            'kind': 'JOINED',
        })

        expect(TimelineMinimapSerializer([obj1, obj2, obj3], many=True).data).to.eq([
            {'kind': 'CR', 'year': 2017},
            {'kind': 'Unit', 'year': 2016},
            {'kind': 'Joined', 'year': 2016}
        ])
