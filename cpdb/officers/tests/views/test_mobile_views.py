from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect

from officers.doc_types import OfficerInfoDocType
from officers.tests.mixins import OfficerSummaryTestCaseMixin


class OfficersMobileViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_retrieve(self):
        OfficerInfoDocType(
            id=123,
            full_name='Alex Mack',
            race='White',
            gender='Male',
            birth_year=1910,
            allegation_count=2,
            complaint_percentile=99.8,
            sustained_count=1,
            percentiles=[
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2002,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
            ]
        ).save()
        self.refresh_read_index()

        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(
            {
                'officer_id': 123,
                'full_name': 'Alex Mack',
                'percentiles': [
                    {
                        'percentile_allegation': '99.345',
                        'percentile_trr': '0.000',
                        'year': 2001,
                        'id': 1,
                        'percentile_allegation_civilian': '98.434',
                        'percentile_allegation_internal': '99.784',
                    },
                    {
                        'percentile_allegation': '99.345',
                        'percentile_trr': '0.000',
                        'year': 2002,
                        'id': 1,
                        'percentile_allegation_civilian': '98.434',
                        'percentile_allegation_internal': '99.784',
                    },
                ],
            }
        )

    def test_retrieve_no_match(self):
        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
