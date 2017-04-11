from datetime import date

from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from officers.indexers import OfficersIndexer


class OfficersIndexerTestCase(SimpleTestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_queryset(self):
        officer = Mock()

        with patch('officers.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficersIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.id = 123
        officer.full_name = 'Alex Mack'
        officer.last_unit = '4'
        officer.rank = '5'
        officer.race = 'White'
        officer.current_badge = '123456'
        officer.gender_display = 'Male'
        officer.appointed_date = date(2017, 2, 27)
        officer.allegation_count = 1
        officer.sustained_count = 0
        officer.complaint_category_aggregation = [
            {
                'name': 'Illegal Search',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_race_aggregation = [
            {
                'name': 'White',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_age_aggregation = [
            {
                'name': '<20',
                'count': 1,
                'sustained_count': 0
            }
        ]
        officer.complainant_gender_aggregation = [
            {
                'name': 'Male',
                'count': 1,
                'sustained_count': 0
            }
        ]

        self.assertDictEqual(OfficersIndexer().extract_datum(officer), {
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': '4',
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'complaint_records': {
                'count': 1,
                'sustained_count': 0,
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 0}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 0}]
                    }
                ]
            }
        })
