from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from data.factories import OfficerFactory, AreaFactory, OfficerBadgeNumberFactory, PoliceUnitFactory
from suggestion.indexers import AutoCompleteIndexer
from es_index import es_client
from suggestion.autocomplete_types import AutoCompleteType


class SuggestionViewSetTestCase(APITestCase):
    def setUp(self):
        self.maxDiff = None

    def test_query_suggestion(self):
        officer_1 = OfficerFactory(first_name='Bb', last_name='Aa')
        officer_2 = OfficerFactory(first_name='Tt', last_name='Bb')
        OfficerFactory(first_name='Cc', last_name='Dd')
        OfficerBadgeNumberFactory(officer=officer_1, current=True, star='1111')
        OfficerBadgeNumberFactory(officer=officer_2, current=False, star='2222')
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'text': 'Bb'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data[AutoCompleteType.OFFICER], [
            {
                'text': 'Bb Aa',
                'score': 1.0,
                'payload': {
                    'url': 'not implemented',
                    'result_text': 'Bb Aa',
                    'result_extra_information': 'Badge 1111'
                }
            },
            {
                'text': 'Tt Bb',
                'score': 1.0,
                'payload': {
                    'url': 'not implemented',
                    'result_text': 'Tt Bb',
                    'result_extra_information': ''
                }
            }
        ])

    def test_query_neighborhoods(self):
        AreaFactory(area_type='other_type', name='Aa')
        AreaFactory(area_type='neighborhoods', name='Aa')
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")
        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'text': 'Aa'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data[AutoCompleteType.NEIGHBORHOODS][0], {
            'text': 'Aa',
            'score': 1.0,
            'payload': {
                'url': 'not implemented',
                'result_text': 'Aa'
            }
        })

    def test_query_officer_unit(self):
        PoliceUnitFactory(unit_name='Aa')
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")
        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'text': 'Aa'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data[AutoCompleteType.OFFICER_UNIT][0], {
            'text': 'Aa',
            'score': 1.0,
            'payload': {
                'url': 'not implemented',
                'result_text': 'Aa'
            }
        })
