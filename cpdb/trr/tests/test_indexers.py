from datetime import date, datetime

from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, PoliceUnitFactory, OfficerHistoryFactory, OfficerAllegationFactory
from trr.factories import TRRFactory, ActionResponseFactory
from trr.indexers import TRRIndexer


class TRRIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        expect(list(TRRIndexer().get_queryset())).to.eq([trr])

    def test_extract_datum(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            first_name='Vinh',
            last_name='Vu',
            race='White',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980)
        OfficerHistoryFactory(officer=officer, unit=unit)
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2003, 1, 1),
            start_date=date(2004, 1, 1),
            end_date=date(2005, 1, 1),
            final_finding='SU')
        trr = TRRFactory(
            trr_datetime=datetime(2001, 1, 1),
            taser=True,
            firearm_used=False,
            officer_assigned_beat='Beat 1',
            officer_in_uniform=True,
            officer_on_duty=False,
            officer=officer,
            subject_gender='M',
            location_recode='Factory',
            subject_age=37,
            block='34XX',
            street='Douglas Blvd',
            beat=1021,
        )

        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Taser', action_sub_category='5.1')
        ActionResponseFactory(trr=trr, force_type='Other', action_sub_category=None, person='Subject Action')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

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
            },

            'subject_race': 'White',
            'subject_gender': 'Male',
            'subject_age': 37,
            'force_category': 'Taser',
            'force_types': [
                'Impact Weapon',
                'Taser',
                'Physical Force - Stunning',
                'Taser Display'
            ],

            'date_of_incident': '2001-01-01',
            'location_type': 'Factory',
            'address': '34XX Douglas Blvd',
            'beat': 1021,
        })

    def test_extract_datum_without_officer(self):
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            trr_datetime=datetime(2001, 1, 1),
            subject_age=37,
            officer_assigned_beat='Beat 1',
            officer_in_uniform=True,
            officer_on_duty=False,
            subject_gender='M',
            officer=None)
        expect(TRRIndexer().extract_datum(trr)).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': None,
            'subject_race': 'White',
            'subject_gender': 'Male',
            'subject_age': 37,
            'force_category': 'Other',
            'force_types': [],
            'date_of_incident': '2001-01-01',
            'location_type': None,
            'address': '',
            'beat': None,
        })

    def test_extract_datum_officer_without_percentile(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            first_name='Vinh',
            last_name='Vu',
            race='White',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980,
            resignation_date=date(2000, 8, 1))
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            trr_datetime=datetime(2001, 1, 1),
            officer_assigned_beat='Beat 1',
            officer_in_uniform=True,
            officer_on_duty=False,
            officer=officer,
            subject_age=37,
            subject_gender='M',
            location_recode='Factory',
            block='34XX',
            street='Douglas Blvd',
            beat=1021,
        )

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
            },
            'subject_race': 'White',
            'subject_gender': 'Male',
            'subject_age': 37,
            'force_category': 'Other',
            'force_types': [],
            'date_of_incident': '2001-01-01',
            'location_type': 'Factory',
            'address': '34XX Douglas Blvd',
            'beat': 1021,
        })
