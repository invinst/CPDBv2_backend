from datetime import datetime, date

from django.test import SimpleTestCase
from mock import Mock
from robber import expect

from officers.serializers import (
    TimelineSerializer, CRTimelineSerializer, OfficerMetricsSerializer, OfficerSummarySerializer
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
            'trr_count': 2,
        })
        expect(OfficerMetricsSerializer(obj).data).to.eq({
            'id': 123,
            'allegation_count': 1,
            'complaint_percentile': 2,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'discipline_count': 5,
            'civilian_compliment_count': 6,
            'trr_count': 2,
        })


class OfficerSummarySerializerTestCase(SimpleTestCase):
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
        })
        expect(OfficerSummarySerializer(obj).data).to.eq({
            'id': 789,
            'unit': {
                'id': 1,
                'unit_name': '',
                'description': ''
            },
            'date_of_appt': '01-01-2010',
            'date_of_resignation': '01-01-2000',
            'active': True,
            'rank': '',
            'full_name': 'Full Name',
            'race': 'Asian',
            'badge': '789',
            'historic_badges': ['123', '456'],
            'gender': 'Male',
            'complaint_records': {
                'count': 2,
                'sustained_count': 1,
                'facets': [
                    {'name': 'category', 'entries': []},
                    {'name': 'complainant race', 'entries': []},
                    {'name': 'complainant age', 'entries': []},
                    {'name': 'complainant gender', 'entries': []},
                ],
                'items': [],
            },
            'birth_year': 1950,
            'current_salary': 90000,
        })

    def test_serialization_with_salary_does_not_exist(self):
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
            'gender_display': 'Male',
            'birth_year': '1950',
            'allegation_count': 2,
            'sustained_count': 1,
            'complaint_category_aggregation': [],
            'complainant_race_aggregation': [],
            'complainant_age_aggregation': [],
            'complainant_gender_aggregation': [],
            'total_complaints_aggregation': [],
            'current_salary': None,
        })
        expect(OfficerSummarySerializer(obj).data).to.eq({
            'id': 789,
            'unit': {
                'id': 1,
                'unit_name': '',
                'description': ''
            },
            'date_of_appt': '01-01-2010',
            'date_of_resignation': '01-01-2000',
            'active': True,
            'rank': '',
            'full_name': 'Full Name',
            'race': 'Asian',
            'badge': '789',
            'historic_badges': ['123', '456'],
            'gender': 'Male',
            'complaint_records': {
                'count': 2,
                'sustained_count': 1,
                'facets': [
                    {'name': 'category', 'entries': []},
                    {'name': 'complainant race', 'entries': []},
                    {'name': 'complainant age', 'entries': []},
                    {'name': 'complainant gender', 'entries': []},
                ],
                'items': [],
            },
            'birth_year': 1950,
            'current_salary': None,
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
