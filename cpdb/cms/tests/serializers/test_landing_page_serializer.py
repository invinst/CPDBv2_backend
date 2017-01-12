from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import LandingPageSerializer
from cms.randomizers import RANDOMIZER_STRATEGIES


class LandingPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        landing_page = Mock()
        landing_page.fields = {
            'reporting_header_value': 'a',
            'reporting_randomizer_pool_size': 10,
            'reporting_randomizer_selected_strategy_id': 1,
            'faq_header_value': 'b',
            'faq_randomizer_pool_size': 10,
            'faq_randomizer_selected_strategy_id': 1,
            'vftg_date_value': 'c',
            'vftg_link_value': 'd',
            'vftg_content_value': 'e',
            'collaborate_header_value': 'f',
            'collaborate_content_value': 'g',
            'about_header_value': 'h',
            'about_content_value': 'i',
            'hero_title_value': 'j',
            'hero_complaint_text_value': 'k',
            'hero_use_of_force_text_value': 'l'
        }
        with patch('cms.serializers.randomize', return_value=[]):
            serializer = LandingPageSerializer(landing_page)
            fields = {
                field['name']: field
                for field in serializer.data['fields']
            }

        self.assertDictEqual(fields['reporting_header'], {
            'name': 'reporting_header',
            'type': 'rich_text',
            'value': 'a'
        })

        self.assertDictEqual(fields['reporting_randomizer'], {
            'name': 'reporting_randomizer',
            'type': 'randomizer',
            'value': {
                'poolSize': 10,
                'selectedStrategyId': 1,
                'strategies': RANDOMIZER_STRATEGIES
            }
        })

        self.assertDictEqual(fields['faq_header'], {
            'name': 'faq_header',
            'type': 'rich_text',
            'value': 'b'
        })

        self.assertDictEqual(fields['hero_title'], {
            'name': 'hero_title',
            'type': 'rich_text',
            'value': 'j'
        })

        self.assertDictEqual(fields['hero_complaint_text'], {
            'name': 'hero_complaint_text',
            'type': 'rich_text',
            'value': 'k'
        })

        self.assertDictEqual(fields['hero_use_of_force_text'], {
            'name': 'hero_use_of_force_text',
            'type': 'rich_text',
            'value': 'l'
        })

        self.assertDictEqual(fields['faq_randomizer'], {
            'name': 'faq_randomizer',
            'type': 'randomizer',
            'value': {
                'poolSize': 10,
                'selectedStrategyId': 1,
                'strategies': RANDOMIZER_STRATEGIES
            }
        })

        self.assertDictEqual(fields['vftg_date'], {
            'name': 'vftg_date',
            'type': 'date',
            'value': 'c'
        })

        self.assertDictEqual(fields['vftg_link'], {
            'name': 'vftg_link',
            'type': 'link',
            'value': 'd'
        })

        self.assertDictEqual(fields['vftg_content'], {
            'name': 'vftg_content',
            'type': 'rich_text',
            'value': 'e'
        })

        self.assertDictEqual(fields['collaborate_header'], {
            'name': 'collaborate_header',
            'type': 'rich_text',
            'value': 'f'
        })

        self.assertDictEqual(fields['collaborate_content'], {
            'name': 'collaborate_content',
            'type': 'rich_text',
            'value': 'g'
        })

        self.assertDictEqual(fields['about_header'], {
            'name': 'about_header',
            'type': 'rich_text',
            'value': 'h'
        })

        self.assertDictEqual(fields['about_content'], {
            'name': 'about_content',
            'type': 'rich_text',
            'value': 'i'
        })

        self.assertDictEqual(fields['reports'], {
            'name': 'reports',
            'type': 'randomized_list',
            'value': []
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            }]
        }
        landing_page = Mock()
        landing_page.save = Mock()
        landing_page.fields = dict()

        serializer = LandingPageSerializer(landing_page, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        landing_page.save.assert_called()
        self.assertDictEqual(landing_page.fields, {
            'vftg_link_type': 'link',
            'vftg_link_value': 'http://abc.xyz'
        })

    def test_create(self):
        data = {
            'fields': [{
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            }]
        }

        with patch('cms.serializers.SlugPage.objects.create') as mock_func:
            serializer = LandingPageSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'vftg_link_type': 'link',
                    'vftg_link_value': 'http://abc.xyz'
                },
                'slug': 'landing-page',
                'serializer_class': 'LandingPageSerializer'
            })
