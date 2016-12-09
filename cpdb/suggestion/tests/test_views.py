from django.core.urlresolvers import reverse
from mock import patch

from rest_framework.test import APITestCase
from rest_framework import status

from suggestion.autocomplete_types import AutoCompleteType
from suggestion.views import SuggestionViewSet


class SuggestionViewSetTestCase(APITestCase):
    @patch('suggestion.views.SuggestionService.suggest')
    def test_retrieve_ok(self, suggester):
        text = 'any_text'
        suggester.return_value = 'anything_suggester_returns'

        url = reverse('api:suggestion-detail', kwargs={
            'text': text
        })
        response = self.client.get(url, {
            'contentType': AutoCompleteType.OFFICER
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'anything_suggester_returns')
        suggester.assert_called_once_with(
            text, limit=SuggestionViewSet.SUGGESTION_PER_TYPE, suggest_content_type=AutoCompleteType.OFFICER)
