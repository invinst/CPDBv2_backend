from datetime import date

from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from officers.indexers import OfficersIndexer


class OfficersIndexerTestCase(SimpleTestCase):
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
        officer.complaint_category_aggregation = [
            {
                'name': 'Illegal Search',
                'count': 1
            }
        ]
        officer.complainant_race_aggregation = [
            {
                'name': 'White',
                'count': 1
            }
        ]
        officer.complainant_age_aggregation = [
            {
                'value': 18,
                'count': 1
            }
        ]
        officer.complainant_gender_aggregation = [
            {
                'name': 'Male',
                'count': 1
            }
        ]

        expect(OfficersIndexer().extract_datum(officer)).to.eq({
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
                'categories': [
                    {
                        'name': 'Illegal Search',
                        'count': 1
                    }
                ],
                'races': [
                    {
                        'name': 'White',
                        'count': 1
                    }
                ],
                'ages': [
                    {
                        'value': 18,
                        'count': 1
                    }
                ],
                'genders': [
                    {
                        'name': 'Male',
                        'count': 1
                    }
                ]
            }
        })
