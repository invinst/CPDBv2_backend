from datetime import date, datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from data.factories import OfficerFactory, PoliceUnitFactory, OfficerHistoryFactory
from trr.factories import TRRFactory, ActionResponseFactory
from trr.indexers import TRRIndexer


class TRRIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        expect(list(TRRIndexer().get_queryset())).to.eq([trr])

    def test_extract_datum(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            id=1,
            first_name='Vinh',
            last_name='Vu',
            race='White',
            rank='Police Officer',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980,
            complaint_percentile=4.4444,
            civilian_allegation_percentile=1.1111,
            internal_allegation_percentile=2.2222,
            trr_percentile=3.3333,
            last_unit=unit
        )
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(
            trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc),
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
            point=Point(1.0, 1.0),
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
                'rank': 'Police Officer',
                'gender': 'Male',
                'resignation_date': None,
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'last_unit': {'unit_name': '001', 'description': 'Unit 001'},
                'id': 1,
                'birth_year': 1980,
                'percentile_allegation': 4.4444,
                'percentile_allegation_civilian': 1.1111,
                'percentile_allegation_internal': 2.2222,
                'percentile_trr': 3.3333,
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
            'point': {
                'lng': 1.0,
                'lat': 1.0,
            },
        })

    def test_extract_datum_without_officer(self):
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc),
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
            'point': None,
        })

    def test_extract_datum_missing_percentile(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            id=1,
            rank='Detective',
            first_name='Vinh',
            last_name='Vu',
            race='White',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980,
            resignation_date=date(2000, 8, 1),
            complaint_percentile=5.5555,
            civilian_allegation_percentile=1.1111,
            internal_allegation_percentile=2.2222,
            last_unit=unit
        )
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc),
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
                'rank': 'Detective',
                'gender': 'Male',
                'resignation_date': '2000-08-01',
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'last_unit': {'unit_name': '001', 'description': 'Unit 001'},
                'id': 1,
                'birth_year': 1980,
                'percentile_allegation': 5.5555,
                'percentile_allegation_civilian': 1.1111,
                'percentile_allegation_internal': 2.2222,
                'percentile_trr': None,
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
            'point': None,
        })
