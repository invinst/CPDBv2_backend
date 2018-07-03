from datetime import datetime

from django.test import SimpleTestCase
from mock import Mock
from robber import expect

from officers.serializers.respone_serialiers import TimelineSerializer, NewTimelineSerializer, OfficerMobileSerializer


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
        expect(TimelineSerializer([obj1, obj2], many=True).data).to.eq([
            {'a': 'b'},
            {'c': 'd'}
        ])


class NewTimelineSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock()
        obj.to_dict = Mock(return_value={
            'a': 'b',
            'c': 'd',
            'date_sort': datetime.now(),
            'priority_sort': 40,
            'officer_id': 123

        })
        expect(NewTimelineSerializer(obj).data).to.eq({
            'a': 'b',
            'c': 'd'
        })

    def test_serialize_multiple(self):
        obj1 = Mock()
        obj1.to_dict = Mock(return_value={
            'a': 'b',
            'date_sort': datetime.now(),
            'priority_sort': 40,
            'officer_id': 123
        })
        obj2 = Mock()
        obj2.to_dict = Mock(return_value={
            'c': 'd',
            'date_sort': datetime.now(),
            'priority_sort': 40,
            'officer_id': 456
        })
        expect(NewTimelineSerializer([obj1, obj2], many=True).data).to.eq([
            {'a': 'b'},
            {'c': 'd'}
        ])


class OfficerMobileSerializerTestCase(SimpleTestCase):
    def test_serialization(self):
        obj = Mock(**{
            'id': 789,
            'last_unit': Mock(id=1, unit_name='', description=''),
            'appointed_date': '01-01-2010',
            'resignation_date': '01-01-2000',
            'get_active_display': Mock(return_value=True),
            'rank': '',
            'full_name': 'Full Name',
            'race': 'Asian',
            'current_badge': '789',
            'historic_badges': ['123', '456'],
            'historic_units': [Mock(**{
                'id': 1,
                'unit_name': '1',
                'description': "Unit 1"
            })],
            'gender_display': 'Male',
            'birth_year': '1950',
            'allegation_count': 2,
            'sustained_count': 1,
            'complaint_category_aggregation': [],
            'complainant_race_aggregation': [],
            'complainant_age_aggregation': [],
            'complainant_gender_aggregation': [],
            'total_complaints_aggregation': [],
            'current_salary': 90000,
            'percentiles': [
                Mock(**{
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                }),
                Mock(**{
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2002,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                }),
            ],
        })
        expect(OfficerMobileSerializer(obj).data).to.eq({
            'officer_id': 789,
            'full_name': 'Full Name',
            'percentiles': [
                {
                    'percentile_allegation': '99.345',
                    'percentile_trr': '0.000',
                    'year': 2001,
                    'id': 1,
                    'percentile_allegation_civilian': '98.434',
                    'percentile_allegation_internal': '99.784',
                },
                {
                    'percentile_allegation': '99.345',
                    'percentile_trr': '0.000',
                    'year': 2002,
                    'id': 1,
                    'percentile_allegation_civilian': '98.434',
                    'percentile_allegation_internal': '99.784',
                },
            ]
        })
