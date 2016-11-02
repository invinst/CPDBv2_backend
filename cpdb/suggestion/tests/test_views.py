from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from data.factories import OfficerFactory, AreaFactory
from suggestion.indexers import AutoCompleteIndexer
from es_index import es_client


class SuggestionViewSetTestCase(APITestCase):
    def setUp(self):
        self.maxDiff = None

    def test_query_suggestion(self):
        OfficerFactory(first_name='Bb', last_name='Aa')
        OfficerFactory(first_name='Tt', last_name='Bb')
        OfficerFactory(first_name='Cc', last_name='Dd')
        AreaFactory(area_type='neighborhoods', name='Bb')
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'text': 'Bb'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['officer_name'][0], {
            'text': 'Bb',
            'length': 2,
            'options': [
                {
                    'text': 'Bb Aa',
                    'score': 1.0,
                    'payload': {
                        'url': 'not implemented',
                        'type': 'OFFICER_NAME'
                    }
                },
                {
                    'text': 'Tt Bb',
                    'score': 1.0,
                    'payload': {
                        'url': 'not implemented',
                        'type': 'OFFICER_NAME'
                    }
                }
            ],
            'offset': 0
        })
        self.assertDictEqual(response.data['neighborhoods'][0], {
            'text': 'Bb',
            'length': 2,
            'options': [
                {
                    'text': 'Bb',
                    'score': 1.0,
                    'payload': {
                        'url': 'not implemented',
                        'type': 'AREA'
                    }
                }
            ],
            'offset': 0
        })

        response = self.client.get(url, {
            'text': 'No result term'
            })
        self.assertDictEqual(response.data['neighborhoods'][0], {
            'length': 14,
            'offset': 0,
            'options': [],
            'text': 'No result term'
        })
        self.assertDictEqual(response.data['officer_name'][0], {
            'length': 14,
            'offset': 0,
            'options': [],
            'text': 'No result term'
        })
        self.assertDictEqual(response.data['officer_badge_number'][0], {
            'length': 14,
            'offset': 0,
            'options': [],
            'text': 'No result term'
        })
