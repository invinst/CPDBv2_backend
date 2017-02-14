from django.test import TestCase
from django.core.management import call_command

from robber import expect

from data.factories import PoliceUnitFactory
from data.management.commands.import_units import DescriptionMatcher


class DescriptionMatcherTestCase(TestCase):
    def test_only_one_candidate(self):
        expect(DescriptionMatcher(context=[{
            'Unit No.': '001',
            'Unit Description': 'description',
            'Status': 'We don\'t care'
        }]).perform('001')).to.be.eq('description')

    def test_multiple_candidates_but_one_active(self):
        expect(DescriptionMatcher(context=[{
            'Unit No.': '001',
            'Unit Description': 'description of inactive one',
            'Status': 'N'
        }, {
            'Unit No.': '001',
            'Unit Description': 'description of active one',
            'Status': 'Y'
        }]).perform('001')).to.be.eq('description of active one')

    def test_multiple_candidates_but_no_active_ones(self):
        expect(DescriptionMatcher(context=[{
            'Unit No.': '001',
            'Unit Description': 'first',
            'Status': 'N'
        }, {
            'Unit No.': '001',
            'Unit Description': 'other',
            'Status': 'N'
        }]).perform('001')).to.be.eq('first')

    def test_multiple_candidates_with_multiple_active_ones(self):
        expect(DescriptionMatcher(context=[{
            'Unit No.': '001',
            'Unit Description': 'first',
            'Status': 'Y'
        }, {
            'Unit No.': '001',
            'Unit Description': 'other',
            'Status': 'Y'
        }]).perform('001')).to.be.eq('first')

    def test_no_candidates(self):
        expect(DescriptionMatcher(context=[]).perform('001')).to.be.eq('')


class CommandTestCase(TestCase):
    def test_handle(self):
        unit = PoliceUnitFactory(unit_name='001', description='')

        call_command('import_units', file_path='cpdb/data/tests/data_sample/units.csv')

        unit.refresh_from_db()
        expect(unit.description).be.eq('District 001')
