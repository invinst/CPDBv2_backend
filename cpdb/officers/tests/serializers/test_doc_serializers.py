from django.test import SimpleTestCase
from mock import Mock
from robber import expect

from officers.serializers.doc_serializers import OfficerSummarySerializer


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
            'historic_units': [Mock(**{
                'id': 1,
                'unit_name': '1',
                'description': 'Unit 1',
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
        })
        expect(OfficerSummarySerializer(obj).data).to.eq({
            'id': 789,
            'unit': {
                'id': 1,
                'unit_name': '',
                'description': '',
                'searchable_unit_name': 'Unit'
            },
            'historic_units': [{
                'id': 1,
                'unit_name': '1',
                'description': 'Unit 1',
                'searchable_unit_name': 'Unit 1',
            }],
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
