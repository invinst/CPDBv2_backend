from django.core.urlresolvers import reverse
from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import OfficerFactory, OfficerAllegationFactory
from .mixins import ReportBottomSheetTestCaseMixin


class ReportBottomSheetOfficerSearchViewTestCase(ReportBottomSheetTestCaseMixin, APITestCase):
    @override_settings(V1_URL='http://cpdb.co')
    def test_retrieve(self):
        officer = OfficerFactory(first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M')
        OfficerAllegationFactory(officer=officer)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:report-bottomsheet-officer-search-detail', kwargs={
            'search_text': 'Kevin Ke'
        }))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'id': 123,
            'full_name': 'Kevin Kerl',
            'v1_url': 'http://cpdb.co/officer/kevin-kerl/123',
            'allegation_count': 1,
            'gender': 'Male',
            'race': 'White'
            }])
