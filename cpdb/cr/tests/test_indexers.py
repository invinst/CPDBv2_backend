from datetime import date

from django.test import SimpleTestCase
from django.contrib.gis.geos import Point

from mock import Mock, patch
from robber import expect

from cr.indexers import CRIndexer


class CRIndexerTestCase(SimpleTestCase):
    def setUp(self):
        super(CRIndexerTestCase, self).setUp()
        self.maxDiff = None

    def test_query_set(self):
        allegation = Mock()

        with patch('cr.indexers.Allegation.objects.all', return_value=[allegation]):
            expect(CRIndexer().get_queryset()).to.eq([allegation])

    def test_extract_datum(self):
        allegation = Mock()
        allegation.crid = '12345'
        allegation.officer_allegations = [
            Mock(
                officer=Mock(id=1, full_name='Mr. Foo', gender_display='Male', race='White'),
                final_finding_display='Sustained', recc_outcome_display='Reprimand', final_outcome_display='Reprimand',
                start_date='2002-02-28', end_date='2003-02-28', category='Operation/Personnel Violations',
                subcategory='NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY'
            )
        ]
        allegation.complainants = [Mock(gender_display='Male', race='White', age=30)]
        allegation.point = Point(12, 21)
        allegation.incident_date = date(2017, 3, 21)
        allegation.address = '3510 Michigan Ave, Chicago, IL 60653'
        allegation.get_location_display = Mock(return_value='Police Building')
        allegation.beat = Mock()
        allegation.beat.name = '23'
        allegation.involvement_set = Mock()
        allegation.involvement_set.filter = Mock(return_value=[Mock(
            involved_type='investigator', officer=Mock(id=1, abbr_name='L. Skol', gender_display='Male', race='White')
        )])

        result = CRIndexer().extract_datum(allegation)
        self.assertEqual(result, {
            'crid': '12345',
            'coaccused': [
                {
                    'id': 1,
                    'full_name': 'Mr. Foo',
                    'gender': 'Male',
                    'race': 'White',
                    'final_finding': 'Sustained',
                    'recc_outcome': 'Reprimand',
                    'final_outcome': 'Reprimand',
                    'category': 'Operation/Personnel Violations',
                    'subcategory': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY',
                    'start_date': '2002-02-28',
                    'end_date': '2003-02-28',
                }
            ],
            'complainants': [{'gender': 'Male', 'race': 'White', 'age': 30}],
            'point': {'long': 12.0, 'lat': 21.0},
            'incident_date': '2017-03-21',
            'address': '3510 Michigan Ave, Chicago, IL 60653',
            'location': 'Police Building',
            'beat': {'name': '23'},
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officers': [{'id': 1, 'abbr_name': 'L. Skol', 'extra_info': 'male, white'}]
                }
            ]
        })
