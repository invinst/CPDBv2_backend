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
        unit = Mock(
            unit_name='001', member_count=2, active_member_count=1, complaint_count=1, sustained_count=0,
            member_race_aggregation=[{'name': 'White', 'count': 1}],
            member_age_aggregation=[{'name': '21-30', 'count': 1}],
            member_gender_aggregation=[{'name': 'Female', 'count': 1}],
            complaint_category_aggregation=[{'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}],
            complainant_race_aggregation=[{'name': 'White', 'count': 1, 'sustained_count': 0}],
            complainant_age_aggregation=[{'name': '21-30', 'count': 1, 'sustained_count': 0}],
            complainant_gender_aggregation=[{'name': 'Female', 'count': 1, 'sustained_count': 0}]
        )

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
