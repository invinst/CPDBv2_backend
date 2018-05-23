from datetime import datetime, date

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import PoliceUnitFactory, OfficerFactory, OfficerHistoryFactory, OfficerAllegationFactory
from trr.factories import TRRFactory
from trr.tests.mixins import TRRTestCaseMixin


class TRRViewSetTestCase(TRRTestCaseMixin, APITestCase):
    def test_retrieve(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(first_name='Vinh', last_name='Vu', race='White', gender='M',
                                 appointed_date=date(2000, 1, 1), birth_year=1980)
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(officer_assigned_beat='Beat 1', officer_in_uniform=True, officer_duty_status=False,
                         officer=officer)
        OfficerAllegationFactory(officer=officer, allegation__incident_date=datetime(2003, 1, 1),
                                 start_date=date(2004, 1, 1), end_date=date(2005, 1, 1), final_finding='SU')

        self.refresh_index()

        response = self.client.get(reverse('api-v2:trr-detail', kwargs={'pk': trr.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_duty_status': False,
            'officer': {
                'id': officer.id,
                'gender': 'Male',
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'unit': {'unit_name': '001', 'description': 'Unit 001'},
                'birth_year': 1980,
                'percentile_trr': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 0.0,
            }
        })

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('api-v2:trr-detail', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
