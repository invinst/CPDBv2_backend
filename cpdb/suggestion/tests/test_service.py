from django.test import TestCase

from data.factories import OfficerFactory, OfficerBadgeNumberFactory, AreaFactory, PoliceUnitFactory
from es_index import es_client
from suggestion.autocomplete_types import AutoCompleteType
from suggestion.indexers import AutoCompleteIndexer
from suggestion.services import SuggestionService


class SuggestionServiceTestCase(TestCase):
    def reindex(self):
        AutoCompleteIndexer().reindex()
        es_client.indices.refresh(index="test_autocompletes")
        self.suggestion_service = SuggestionService()

    def test_suggest_officers(self):
        officer_1 = OfficerFactory(first_name='Bb', last_name='Aa')
        officer_2 = OfficerFactory(first_name='Tt', last_name='Bb')
        OfficerFactory(first_name='Cc', last_name='Dd')
        OfficerBadgeNumberFactory(officer=officer_1, current=True, star='1111')
        OfficerBadgeNumberFactory(officer=officer_2, current=False, star='2222')
        self.reindex()

        results = self.suggestion_service.suggest('Bb')
        self.assertListEqual(results[AutoCompleteType.OFFICER], [
            {
                'text': 'Bb Aa',
                'score': 1.0,
                'payload': {
                    'url': 'https://beta.cpdb.co/officer/bb-aa/%s' % officer_1.pk,
                    'result_text': 'Bb Aa',
                    'result_extra_information': 'Badge # 1111'
                }
            },
            {
                'text': 'Tt Bb',
                'score': 1.0,
                'payload': {
                    'url': 'https://beta.cpdb.co/officer/tt-bb/%s' % officer_2.pk,
                    'result_text': 'Tt Bb',
                    'result_extra_information': ''
                }
            }
        ])

    def test_suggest_only_neighborhoods(self):
        AreaFactory(area_type='other_type', name='Aa')
        AreaFactory(area_type='neighborhoods', name='Aa')
        self.reindex()

        results = self.suggestion_service.suggest('Aa')
        self.assertDictEqual(results[AutoCompleteType.NEIGHBORHOOD][0], {
            'text': 'Aa',
            'score': 1.0,
            'payload': {
                'url': 'https://beta.cpdb.co/url-mediator/session-builder?neighborhood=Aa',
                'result_text': 'Aa'
            }
        })

    def test_suggest_officer_unit(self):
        PoliceUnitFactory(unit_name='Aa')
        self.reindex()

        results = self.suggestion_service.suggest('Aa')
        self.assertDictEqual(results[AutoCompleteType.OFFICER_UNIT][0], {
            'text': 'Aa',
            'score': 1.0,
            'payload': {
                'url': 'https://beta.cpdb.co/url-mediator/session-builder?unit=Aa',
                'result_text': 'Aa'
            }
        })

    def test_suggest_community_area(self):
        AreaFactory(area_type='other_type', name='Aa')
        AreaFactory(area_type='community', name='Aa')

        self.reindex()

        results = self.suggestion_service.suggest('Aa')
        self.assertDictEqual(results[AutoCompleteType.COMMUNITY][0], {
            'text': 'Aa',
            'score': 1.0,
            'payload': {
                'url': 'https://beta.cpdb.co/url-mediator/session-builder?community=Aa',
                'result_text': 'Aa'
            }
        })

    def test_suggest_single_type(self):
        OfficerFactory(first_name='Lorem')
        AreaFactory(area_type='neighborhoods', name='Lorem')
        self.reindex()

        results = self.suggestion_service.suggest('Lorem', suggest_content_type=AutoCompleteType.OFFICER)
        result_keys = [key for key in results]
        self.assertEqual(len(result_keys), 1)
        self.assertEqual(result_keys[0], AutoCompleteType.OFFICER)
