import urllib

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory,
    AllegationCategoryFactory
)
from .mixins import CRTestCaseMixin


class CRViewSetRelatedComplaintsTestCase(CRTestCaseMixin, APITestCase):
    def setUp(self):
        super(CRViewSetRelatedComplaintsTestCase, self).setUp()

    def test_allegation_has_no_point(self):
        allegation = AllegationFactory(point=None)

        response = self.client.get(reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            "count": 0,
            "previous": None,
            "next": None,
            "results": []
        })

    def test_missing_params(self):
        allegation = AllegationFactory(point=Point([0, 0]))

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'officers'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'distance': '10mi'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_invalid_params(self):
        allegation = AllegationFactory(point=Point([0, 0]))

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'allegation',
                    'distance': '10mi'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'officers',
                    'distance': '100km'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'officers',
                    'distance': '10mi',
                    'offset': 'abc'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'officers',
                    'distance': '100km',
                    'limit': 'abc'
                })
            )
        )
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_query_match_categories(self):
        allegation = AllegationFactory(point=Point([0, 0]))
        allegation_category = AllegationCategoryFactory(category='False Arrest')
        OfficerAllegationFactory(
            allegation=allegation,
            allegation_category=allegation_category
        )

        related_allegation = AllegationFactory(point=Point([0.01, 0.01]))
        officer2 = OfficerFactory(first_name='T.', last_name='Parker')
        ComplainantFactory(allegation=related_allegation, gender='M', race='Black', age='18')
        OfficerAllegationFactory(
            officer=officer2, allegation=related_allegation,
            allegation_category=allegation_category
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=related_allegation,
            allegation_category=AllegationCategoryFactory(category='Use Of Force')
        )

        self.refresh_index()

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'categories',
                    'distance': '10mi'
                })
            )
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            "count": 1,
            "previous": None,
            "next": None,
            "results": [{
                "crid": str(related_allegation.crid),
                "coaccused": [
                    "T. Parker"
                ],
                "category_names": [
                    "False Arrest",
                ],
                "complainants": [{
                    "race": "Black",
                    "gender": "Male",
                    "age": 18
                }]
            }]
        })

    def test_query_match_officers(self):
        allegation = AllegationFactory(point=Point([0, 0]))
        allegation_category = AllegationCategoryFactory(category='False Arrest')
        OfficerAllegationFactory(
            allegation=allegation,
            allegation_category=allegation_category
        )

        related_allegation = AllegationFactory(point=Point([0.01, 0.01]))
        officer2 = OfficerFactory(first_name='T.', last_name='Parker')
        ComplainantFactory(allegation=related_allegation, gender='M', race='Black', age='18')
        OfficerAllegationFactory(
            officer=officer2, allegation=related_allegation,
            allegation_category=allegation_category
        )

        self.refresh_index()

        response = self.client.get(
            '%s?%s' % (
                reverse('api-v2:cr-related-complaints', kwargs={'pk': allegation.crid}),
                urllib.urlencode({
                    'match': 'categories',
                    'distance': '10mi'
                })
            )
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            "count": 1,
            "previous": None,
            "next": None,
            "results": [{
                "crid": str(related_allegation.crid),
                "coaccused": [
                    "T. Parker"
                ],
                "category_names": [
                    "False Arrest",
                ],
                "complainants": [{
                    "race": "Black",
                    "gender": "Male",
                    "age": 18
                }]
            }]
        })
