from datetime import date, datetime

from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, PoliceUnitFactory, OfficerHistoryFactory, OfficerAllegationFactory
from trr.factories import TRRFactory
from trr.indexers import TRRIndexer


class TRRIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        expect(list(TRRIndexer().get_queryset())).to.eq([trr])

    def test_extract_datum(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(first_name='Vinh', last_name='Vu', race='White', gender='M',
                                 appointed_date=date(2000, 1, 1), birth_year=1980)
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(officer_assigned_beat='Beat 1', officer_in_uniform=True, officer_on_duty=False,
                         officer=officer)
        OfficerAllegationFactory(officer=officer, allegation__incident_date=datetime(2003, 1, 1),
                                 start_date=date(2004, 1, 1), end_date=date(2005, 1, 1), final_finding='SU')

        indexer = TRRIndexer()
        expect(indexer.extract_datum(trr)).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': {
                'gender': 'Male',
                'resignation_date': None,
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'last_unit': {'unit_name': '001', 'description': 'Unit 001'},
                'id': officer.id,
                'birth_year': 1980,
                'percentile_trr': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 0.0,
            }
        })

    def test_extract_datum_without_officer(self):
        trr = TRRFactory(officer_assigned_beat='Beat 1', officer_in_uniform=True, officer_on_duty=False,
                         officer=None)
        expect(TRRIndexer().extract_datum(trr)).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': None
        })

    def test_extract_datum_officer_without_percentile(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(first_name='Vinh', last_name='Vu', race='White', gender='M',
                                 appointed_date=date(2000, 1, 1), birth_year=1980, resignation_date=date(2000, 8, 1))
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(officer_assigned_beat='Beat 1', officer_in_uniform=True, officer_on_duty=False,
                         officer=officer)

        indexer = TRRIndexer()
        expect(indexer.extract_datum(trr)).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': {
                'gender': 'Male',
                'resignation_date': '2000-08-01',
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'last_unit': {'unit_name': '001', 'description': 'Unit 001'},
                'id': officer.id,
                'birth_year': 1980,
            }
        })
