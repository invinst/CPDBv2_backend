from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from units.indexers import UnitIndexer


class UnitIndexerTestCase(SimpleTestCase):

    def test_get_queryset(self):
        unit = Mock()
        with patch('units.indexers.PoliceUnit.objects.all', return_value=[unit]):
            expect(UnitIndexer().get_queryset()).to.eq([unit])

    def test_extract_datum(self):
        unit = Mock()
        unit.unit_name = '001'
        unit.member_count = 2
        unit.active_member_count = 1
        unit.complaint_count = 1
        unit.sustained_count = 0
        unit.member_race_aggregation = [
            {
                'name': 'White',
                'count': 1
            }
        ]
        unit.member_age_aggregation = [
            {
                'name': '21-30',
                'count': 1
            }
        ]
        unit.member_gender_aggregation = [
            {
                'name': 'Female',
                'count': 1
            }
        ]
        unit.complaint_category_aggregation = [
            {
                'name': 'Illegal Search',
                'count': 1,
                'sustained_count': 0
            }
        ]
        unit.complainant_race_aggregation = [
            {
                'name': 'White',
                'count': 1,
                'sustained_count': 0
            }
        ]
        unit.complainant_age_aggregation = [
            {
                'name': '21-30',
                'count': 1,
                'sustained_count': 0
            }
        ]
        unit.complainant_gender_aggregation = [
            {
                'name': 'Female',
                'count': 1,
                'sustained_count': 0
            }
        ]

        expect(UnitIndexer().extract_datum(unit)).to.eq({
            'unit_name': '001',
            'member_records': {
                'active_members': 1,
                'total': 2,
                'facets': [
                    {'name': 'race', 'entries': [{'name': 'White', 'count': 1}]},
                    {'name': 'age', 'entries': [{'name': '21-30', 'count': 1}]},
                    {'name': 'gender', 'entries': [{'name': 'Female', 'count': 1}]},
                ]
            },
            'complaint_records': {
                'count': 1,
                'sustained_count': 0,
                'facets': [
                    {'name': 'category', 'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}]},
                    {'name': 'race', 'entries': [{'name': 'White', 'count': 1, 'sustained_count': 0}]},
                    {'name': 'age', 'entries': [{'name': '21-30', 'count': 1, 'sustained_count': 0}]},
                    {'name': 'gender', 'entries': [{'name': 'Female', 'count': 1, 'sustained_count': 0}]},
                ]
            }
        })
