from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from data.factories import OfficerFactory
from suggestion.indexers import AutoCompleteIndexer
from es_index import es_client


class SuggestionViewSetTestCase(APITestCase):
    def setUp(self):
        self.maxDiff = None

    def test_query_suggestion(self):
        OfficerFactory(full_name='Bb Aa')
        OfficerFactory(full_name='Tt Bb')
        OfficerFactory(full_name='Cc Dd')
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'text': 'Bb'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
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

        response = self.client.get(url, {
            'text': 'No result term'
            })
        self.assertDictEqual(response.data, {
            'text': 'No result term',
            'length': 14,
            'options': [],
            'offset': 0
        })
