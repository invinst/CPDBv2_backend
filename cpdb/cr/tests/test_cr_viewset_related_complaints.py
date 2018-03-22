import urllib

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory
)
from .mixins import CRTestCaseMixin


class CRViewSetRelatedComplaintsTestCase(CRTestCaseMixin, APITestCase):
    def setUp(self):
        super(CRViewSetRelatedComplaintsTestCase, self).setUp()
        self.allegation = AllegationFactory(point=Point([0, 0]))

    def search(self, crid, params):
        return self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': crid}),
                urllib.urlencode(params)
            )
        )

    def test_allegation_has_no_point(self):
        allegation = AllegationFactory(point=None)

        response = self.search(allegation.crid, {})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            "count": 0,
            "previous": None,
            "next": None,
            "results": []
        })

    def test_missing_params(self):
        response = self.search(self.allegation.crid, {'match': 'officers'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = response = self.search(self.allegation.crid, {'distance': '10mi'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_invalid_params(self):
        response = self.search(self.allegation.crid, {
            'match': 'allegation',
            'distance': '10mi'
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '100km'
        })
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '10mi',
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
        ComplainantFactory(allegation=complaint.allegation, gender='M', race='Black', age='18')
        OfficerAllegationFactory(
            allegation__point=Point([1, 1]),
            allegation_category__category='False Arrest'
        )

        self.refresh_index()

        response = self.search(self.allegation.crid, {
            'match': 'categories',
            'distance': '1mi'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

    def test_query_matching_allegation_with_same_categories(self):
        OfficerAllegationFactory(
            allegation=self.allegation,
            allegation_category__category='False Arrest'
        )
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            allegation_category__category='False Arrest'
        )
        ComplainantFactory(allegation=complaint.allegation, gender='M', race='Black', age='18')
        OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            allegation_category__category='Use Of Force'
        )

        self.refresh_index()

        response = self.search(self.allegation.crid, {
            'match': 'categories',
            'distance': '1mi'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

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

        self.refresh_index()

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '1mi'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['crid']).to.eq(str(complaint.allegation.crid))

    def test_return_correct_response(self):
        officer = OfficerFactory(first_name='John', last_name='Hurley')
        OfficerAllegationFactory(
            allegation=self.allegation,
            officer=officer
        )
        complaint = OfficerAllegationFactory(
            allegation__point=Point([0.01, 0.01]),
            officer=officer,
            allegation_category__category='False Arrest'
        )
        ComplainantFactory(allegation=complaint.allegation, gender='M', race='Black', age='18')

        self.refresh_index()

        response = self.search(self.allegation.crid, {
            'match': 'officers',
            'distance': '10mi'
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'crid': str(complaint.allegation.crid),
                'coaccused': [
                    'John Hurley'
                ],
                'category_names': [
                    'False Arrest',
                ],
                'complainants': [{
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 18
                }]
            }]
        })
