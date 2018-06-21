from datetime import date, datetime

import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect

from officers.tests.mixins import OfficerSummaryTestCaseMixin
from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory, ComplainantFactory,
    SalaryFactory
)
from trr.factories import TRRFactory


class OfficersMobileViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_retrieve(self):

        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2002, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1910, complaint_percentile=32.5
        )
        allegation = AllegationFactory(incident_date=datetime(2002, 3, 1, tzinfo=pytz.utc))
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(
            officer=officer, effective_date=datetime(2002, 2, 27, tzinfo=pytz.utc),
            unit=PoliceUnitFactory(id=1, unit_name='CAND', description='')
        )
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerBadgeNumberFactory(officer=officer, star='789', current=False)
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category,
            final_finding='SU', start_date=date(2002, 3, 2), disciplined=True
        )
        AwardFactory(officer=officer, award_type='Complimentary Letter', start_date=date(2014, 5, 1))
        AwardFactory(officer=officer, award_type='Honored Police Star', start_date=date(2014, 6, 1))
        AwardFactory(officer=officer, award_type='Honorable Mention', start_date=date(2014, 7, 1))
        SalaryFactory(officer=officer, salary=50000, year=2002)
        SalaryFactory(officer=officer, salary=90000, year=2017)
        TRRFactory(officer=officer, trr_datetime=datetime(2002, 3, 1, tzinfo=pytz.utc))

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 123}))
        expected_response = {
            'officer_id': 123,
            'unit': {
                'unit_id': 1,
                'unit_name': 'CAND',
                'description': '',
            },
            'percentiles': [
                {
                    'id': 123,
                    'year': 2001,
                    'percentile_trr': u'0.000',
                    'percentile_allegation': u'0.000',
                    'percentile_allegation_civilian': u'0.000',
                    'percentile_allegation_internal': u'0.000'
                },
                {
                    'id': 123,
                    'year': 2002,
                    'percentile_trr': u'0.000',
                    'percentile_allegation': u'0.000',
                    'percentile_allegation_civilian': u'0.000',
                    'percentile_allegation_internal': u'0.000'
                },
            ],
            'date_of_appt': '2002-02-27',
            'date_of_resignation': '2017-12-27',
            'active': True,
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['789'],
            'gender': 'Male',
            'birth_year': 1910,
            'sustained_count': 1,
            'civilian_compliment_count': 1,
            'allegation_count': 1,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'trr_count': 1,
            'major_award_count': 1,
            'complaint_percentile': 32.5,
            'honorable_mention_percentile': 0.0,
        }
        expect(response.data).to.eq(expected_response)

    def test_retrieve_no_match(self):
        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
