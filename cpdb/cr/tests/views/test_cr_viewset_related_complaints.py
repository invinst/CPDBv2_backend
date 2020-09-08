from urllib.parse import urlencode
from datetime import datetime
from operator import itemgetter

from django.urls import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status

import pytz
from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory
)


class CRViewSetRelatedComplaintsTestCase(APITestCase):
    def setUp(self):
        super(CRViewSetRelatedComplaintsTestCase, self).setUp()
        self.allegation = AllegationFactory(point=Point([0, 0]))

    def search(self, crid, params):
        return self.client.get(
            f"{reverse('api-v2:cr-related-complaints', kwargs={'pk': crid})}?{urlencode(params)}"
        )

    def expect_empty_result(self, response):
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 0,
            'previous': None,
            'next': None,
            'results': []
        })

    def test_allegation_has_no_point(self):
        OfficerAllegationFactory(allegation=self.allegation)
        allegation = AllegationFactory(point=None)

        response = self.search(allegation.crid, {
            'distance': 10,
            'match': 'categories'
        })
        self.expect_empty_result(response)

    def test_allegation_has_no_link_to_officer(self):
        response = self.search(self.allegation.crid, {
            'distance': 10,
            'match': 'officers'
        })
        self.expect_empty_result(response)

    def test_allegation_has_no_category(self):
        OfficerAllegationFactory(allegation=self.allegation, allegation_category=None)

        response = self.search(self.allegation.crid, {
            'distance': 10,
            'match': 'categories'
        })
        self.expect_empty_result(response)

    def test_allegation_has_no_coaccused(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest')
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation__point=Point(0.1, 0.1),
            allegation_category__category='False Arrest')
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            allegation_category__category='False Arrest'
        )

        response = self.search(self.allegation.crid, {
            'distance': 10,
            'match': 'categories'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

    def test_allegation_has_no_complainant(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest')
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            allegation_category__category='False Arrest'
        )

        response = self.search(self.allegation.crid, {
            'distance': 10,
            'match': 'categories'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))
        expect(response.data['results'][0]['complainants']).to.have.length(0)

    def test_missing_params(self):
        response = self.search(self.allegation.crid, {'match': 'officers'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {'distance': 10})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_invalid_params(self):
        response = self.search(self.allegation.crid, {
            'match': 'allegation',
            'distance': 10
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '100km'
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': 10,
            'offset': 'abc'
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '100km',
            'limit': 'abc'
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_query_not_matching_allegation_too_far_away(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest'
        )
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            allegation_category__category='False Arrest'
        )
        OfficerAllegationFactory(
            allegation__point=Point([1, 1]),
            allegation_category__category='False Arrest'
        )

        response = self.search(self.allegation.crid, {
            'match': 'categories',
            'distance': 1
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

    def test_query_matching_allegation_with_same_categories(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest'
        )
        related_complaint = AllegationFactory(point=Point([0.01, 0.01]))
        other_complaint = AllegationFactory(point=Point([0.01, 0.01]))

        OfficerAllegationFactory(allegation=related_complaint, allegation_category__category='False Arrest')
        OfficerAllegationFactory(allegation=other_complaint, allegation_category__category='Use Of Force')

        response = self.search(self.allegation.crid, {
            'match': 'categories',
            'distance': 1
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(related_complaint.crid))

    def test_query_matching_allegation_with_same_officers(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(
            allegation=self.allegation,
            officer=officer
        )
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            officer=officer
        )
        ComplainantFactory(allegation=complaint.allegation, gender='M', race='Black', age='18')
        OfficerAllegationFactory(allegation__point=Point([0.01, 0.01]))

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': 1
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

    def test_order_with_distance(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest'
        )
        related_complaint_1 = AllegationFactory(point=Point([0.005, 0.009]))
        related_complaint_2 = AllegationFactory(point=Point([0.004, 0.006]))
        related_complaint_3 = AllegationFactory(point=Point([0.01, 0.01]))

        OfficerAllegationFactory(allegation=related_complaint_1, allegation_category__category='False Arrest')
        OfficerAllegationFactory(allegation=related_complaint_2, allegation_category__category='False Arrest')
        OfficerAllegationFactory(allegation=related_complaint_3, allegation_category__category='False Arrest')

        response = self.search(self.allegation.crid, {
            'match': 'categories',
            'distance': 1
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(3)
        expected_crids = [related_complaint_2.crid, related_complaint_1.crid, related_complaint_3.crid]
        expect([item['crid'] for item in response.data['results']]).to.eq(expected_crids)

    def test_return_correct_response(self):
        officer_1 = OfficerFactory(first_name='Jos', last_name='Parker')
        officer_2 = OfficerFactory(first_name='John', last_name='Hurley')
        OfficerAllegationFactory(
            allegation=self.allegation,
            officer=officer_1
        )
        related_allegation = AllegationFactory(
            point=Point([0.01, 0.01]),
            incident_date=datetime(2016, 2, 23, tzinfo=pytz.utc),
        )
        OfficerAllegationFactory(
            allegation=related_allegation,
            officer=officer_1,
            allegation_category__category='False Arrest'
        )
        OfficerAllegationFactory(
            allegation=related_allegation,
            officer=officer_2,
            allegation_category__category='Use of Force'
        )
        ComplainantFactory(allegation=related_allegation, gender='M', race='Black', age='18')
        ComplainantFactory(allegation=related_allegation, gender='F', race='Black', age='19')

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': 10
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        response_data = response.data
        first_result = response_data['results'][0]
        first_result['coaccused'] = sorted(first_result['coaccused'])
        first_result['complainants'] = sorted(first_result['complainants'], key=itemgetter('gender'))

        expect(response_data).to.eq({
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'crid': related_allegation.crid,
                'coaccused': [
                    'J. Hurley',
                    'J. Parker'
                ],
                'category_names': [
                    'False Arrest', 'Use of Force'
                ],
                'complainants': [
                    {
                        'race': 'Black',
                        'gender': 'Female',
                        'age': 19
                    },
                    {
                        'race': 'Black',
                        'gender': 'Male',
                        'age': 18
                    }
                ],
                'point': {
                    'lat': 0.01,
                    'lon': 0.01
                },
                'incident_date': '2016-02-23',
            }]
        })
