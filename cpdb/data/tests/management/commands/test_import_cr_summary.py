from django.test import TestCase
from django.core.management import call_command

from robber import expect

from data.factories import AllegationFactory


class CommandTestCase(TestCase):
    def test_handle(self):
        allegation = AllegationFactory(crid='001')

        call_command('import_cr_summary', file_path='cpdb/data/tests/data_sample/cr_summary.csv')

        allegation.refresh_from_db()
        expect(allegation.summary).be.eq('Summary Text 01 is here')
