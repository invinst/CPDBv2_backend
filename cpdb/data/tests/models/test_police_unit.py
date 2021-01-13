from datetime import datetime
from operator import itemgetter

import pytz
from django.test.testcases import TestCase, override_settings

from robber.expect import expect
from freezegun import freeze_time

from data.models import PoliceUnit
from data.factories import (
    OfficerFactory, OfficerHistoryFactory, PoliceUnitFactory, AllegationFactory, OfficerAllegationFactory,
    AllegationCategoryFactory, ComplainantFactory
)


class PoliceUnitTestCase(TestCase):
    def test_str(self):
        self.assertEqual(str(PoliceUnit(unit_name='lorem')), 'lorem')

    def test_v2_to(self):
        unit = '011'
        to = '/unit/011/'
        expect(PoliceUnit(unit_name=unit).v2_to).to.eq(to)

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        unit = 'unit'
        url = 'domain/url-mediator/session-builder?unit=unit'
        expect(PoliceUnit(unit_name=unit).v1_url).to.eq(url)

    def test_member_count(self):
        unit = PoliceUnitFactory()
        OfficerHistoryFactory(officer=OfficerFactory(), unit=unit)
        OfficerHistoryFactory(officer=OfficerFactory(), unit=unit)
        expect(unit.member_count).to.eq(2)

    def test_member_count_in_case_officer_left_and_rejoin(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer = OfficerFactory()
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=officer, unit=unit2)
        OfficerHistoryFactory(officer=officer, unit=unit1)
        expect(unit1.member_count).to.eq(1)
        expect(unit2.member_count).to.eq(1)

    def test_active_member_count(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer = OfficerFactory()
        OfficerHistoryFactory(officer=officer, unit=unit1, end_date=datetime(2011, 1, 1, tzinfo=pytz.utc))
        OfficerHistoryFactory(officer=officer, unit=unit2, end_date=datetime(2011, 2, 1, tzinfo=pytz.utc))
        OfficerHistoryFactory(officer=officer, unit=unit1, end_date=None)
        expect(unit1.active_member_count).to.eq(1)
        expect(unit2.active_member_count).to.eq(0)

    def test_member_race_aggregation(self):
        unit = PoliceUnitFactory()
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(race='White'))
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(race=''))
        expect(sorted(unit.member_race_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': 'Unknown',
                'count': 1
            },
            {
                'name': 'White',
                'count': 1
            }
        ])

    def test_member_race_aggregation_in_case_officer_left_and_rejoin(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer = OfficerFactory(race='White')
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=officer, unit=unit2)
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(race='White'), unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(race=''), unit=unit1)

        expect(sorted(unit1.member_race_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': 'Unknown',
                'count': 1
            },
            {
                'name': 'White',
                'count': 2
            }
        ])

    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_member_age_aggregation(self):
        unit = PoliceUnitFactory()
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(birth_year='1980'))
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(birth_year=None))
        expect(sorted(unit.member_age_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': '31-40',
                'count': 1
            },
            {
                'name': 'Unknown',
                'count': 1
            }
        ])

    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_member_age_aggregation_in_case_officer_left_and_rejoin(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer = OfficerFactory(birth_year='1980')
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=officer, unit=unit2)
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(birth_year='1985'), unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(birth_year=None), unit=unit1)

        expect(sorted(unit1.member_age_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': '31-40',
                'count': 2
            },
            {
                'name': 'Unknown',
                'count': 1
            }
        ])

    def test_member_gender_aggregation(self):
        unit = PoliceUnitFactory()
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(gender='F'))
        OfficerHistoryFactory(unit=unit, officer=OfficerFactory(gender=''))
        expect(sorted(unit.member_gender_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': 'Female',
                'count': 1
            },
            {
                'name': 'Unknown',
                'count': 1
            }
        ])

    def test_member_gender_aggregation_in_case_officer_left_and_rejoin(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer = OfficerFactory(gender='F')
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=officer, unit=unit2)
        OfficerHistoryFactory(officer=officer, unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(gender='F'), unit=unit1)
        OfficerHistoryFactory(officer=OfficerFactory(gender=''), unit=unit1)

        expect(sorted(unit1.member_gender_aggregation, key=itemgetter('name'))).to.eq([
            {
                'name': 'Female',
                'count': 2
            },
            {
                'name': 'Unknown',
                'count': 1
            }
        ])

    def test_complaint_count(self):
        unit1 = PoliceUnitFactory()
        unit2 = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        OfficerHistoryFactory(unit=unit1, officer=officer1)
        OfficerHistoryFactory(unit=unit2, officer=officer2)
        OfficerAllegationFactory(officer=officer1)
        expect(unit1.complaint_count).to.eq(1)
        expect(unit2.complaint_count).to.eq(0)

    def test_complaint_count_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        OfficerHistoryFactory(unit=unit, officer=officer1)
        OfficerHistoryFactory(unit=unit, officer=officer2)
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)

        expect(unit.complaint_count).to.eq(1)

    def test_sustained_count(self):
        unit = PoliceUnitFactory()
        officer = OfficerFactory()
        OfficerHistoryFactory(unit=unit, officer=officer)
        OfficerAllegationFactory(officer=officer, final_finding='SU')
        OfficerAllegationFactory(officer=officer, final_finding='UN')
        expect(unit.sustained_count).to.eq(1)

    def test_sustained_count_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        OfficerHistoryFactory(unit=unit, officer=officer1)
        OfficerHistoryFactory(unit=unit, officer=officer2)
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer1, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer2, allegation=allegation, final_finding='SU')

        expect(unit.sustained_count).to.eq(1)

    def test_complaint_category_aggregation(self):
        unit = PoliceUnitFactory()
        officer = OfficerFactory()
        OfficerHistoryFactory(unit=unit, officer=officer)
        OfficerAllegationFactory(
            officer=officer,
            allegation_category=AllegationCategoryFactory(category='Use of Force'),
            final_finding='NS'
        )
        expect(unit.complaint_category_aggregation).to.eq([{
            'name': 'Use of Force',
            'count': 1,
            'sustained_count': 0
        }])

    def test_complaint_category_aggregation_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer1, unit=unit)
        OfficerHistoryFactory(officer=officer2, unit=unit)
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation, allegation_category=allegation_category, final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation, allegation_category=allegation_category, final_finding='NS'
        )
        expect(unit.complaint_category_aggregation).to.eq([{
            'name': 'Use of Force',
            'count': 1,
            'sustained_count': 0
        }])

    def test_complainant_race_aggregation(self):
        unit = PoliceUnitFactory()
        officer = OfficerFactory()
        allegation = AllegationFactory()
        OfficerHistoryFactory(unit=unit, officer=officer)
        OfficerAllegationFactory(officer=officer, allegation=allegation, final_finding='NS')
        ComplainantFactory(allegation=allegation, race='White')
        expect(unit.complainant_race_aggregation).to.eq([{
            'name': 'White',
            'count': 1,
            'sustained_count': 0
        }])

    def test_complainant_race_aggregation_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation = AllegationFactory()
        OfficerHistoryFactory(officer=officer1, unit=unit)
        OfficerHistoryFactory(officer=officer2, unit=unit)
        OfficerAllegationFactory(officer=officer1, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer2, allegation=allegation, final_finding='SU')
        ComplainantFactory(allegation=allegation, race='Black')
        expect(unit.complainant_race_aggregation).to.eq([{
            'name': 'Black',
            'count': 1,
            'sustained_count': 1
        }])

    def test_complainant_age_aggregation(self):
        unit = PoliceUnitFactory()
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerHistoryFactory(officer=officer, unit=unit)
        OfficerAllegationFactory(officer=officer, allegation=allegation1, final_finding='SU')
        OfficerAllegationFactory(officer=officer, allegation=allegation2, final_finding='UN')
        ComplainantFactory(allegation=allegation1, age=25)
        ComplainantFactory(allegation=allegation2, age=None)
        expect(unit.complainant_age_aggregation).to.eq([{
            'name': '21-30',
            'count': 1,
            'sustained_count': 1
        }, {
            'name': 'Unknown',
            'count': 1,
            'sustained_count': 0
        }])

    def test_complainant_age_aggregation_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation = AllegationFactory()
        OfficerHistoryFactory(officer=officer1, unit=unit)
        OfficerHistoryFactory(officer=officer2, unit=unit)
        OfficerAllegationFactory(officer=officer1, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer2, allegation=allegation, final_finding='SU')
        ComplainantFactory(allegation=allegation, age=25)
        expect(unit.complainant_age_aggregation).to.eq([{
            'name': '21-30',
            'count': 1,
            'sustained_count': 1
        }])

    def test_complainant_gender_aggregation(self):
        unit = PoliceUnitFactory()
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerHistoryFactory(officer=officer, unit=unit)
        OfficerAllegationFactory(officer=officer, allegation=allegation1, final_finding='SU')
        OfficerAllegationFactory(officer=officer, allegation=allegation2, final_finding='UN')
        ComplainantFactory(allegation=allegation1, gender='F')
        ComplainantFactory(allegation=allegation2, gender='')
        expect(sorted(unit.complainant_gender_aggregation, key=itemgetter('name'))).to.eq([{
            'name': 'Female',
            'count': 1,
            'sustained_count': 1
        }, {
            'name': 'Unknown',
            'count': 1,
            'sustained_count': 0
        }])

    def test_complainant_gender_aggregation_with_duplicated_allegation(self):
        unit = PoliceUnitFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation = AllegationFactory()
        OfficerHistoryFactory(officer=officer1, unit=unit)
        OfficerHistoryFactory(officer=officer2, unit=unit)
        OfficerAllegationFactory(officer=officer1, allegation=allegation, final_finding='SU')
        OfficerAllegationFactory(officer=officer2, allegation=allegation, final_finding='SU')
        ComplainantFactory(allegation=allegation, gender='F')
        expect(unit.complainant_gender_aggregation).to.eq([{
            'name': 'Female',
            'count': 1,
            'sustained_count': 1
        }])

    def test_get_absolute_url(self):
        expect(PoliceUnit(unit_name='011').v2_to).to.eq('/unit/011/')
