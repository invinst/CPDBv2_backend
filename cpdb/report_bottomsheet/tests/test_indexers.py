from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from report_bottomsheet.indexers import OfficerIndexer


class OfficerIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()

        with patch('report_bottomsheet.indexers.Officer.objects.all', return_value=[officer]):
            expect(OfficerIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock()
        officer.id = 123
        officer.allegation_count = 23
        officer.full_name = 'Alex Mack'
        officer.v1_url = 'http://cpdb.co/officer/alex/123'
        officer.gender_display = 'Female'
        officer.race = 'White'

        expect(OfficerIndexer().extract_datum(officer)).to.eq({
            'id': 123,
            'allegation_count': 23,
            'full_name': 'Alex Mack',
            'v1_url': 'http://cpdb.co/officer/alex/123',
            'gender': 'Female',
            'race': 'White'
        })
