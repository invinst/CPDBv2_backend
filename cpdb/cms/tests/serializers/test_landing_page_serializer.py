from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import LandingPageSerializer


class LandingPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        landing_page = Mock()
        landing_page.fields = {
            'navbar_title_value': 'a',
            'navbar_subtitle_value': 'b',
            'demo_video_text_value': 'What is CPDP?'
        }

        serializer = LandingPageSerializer(landing_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }

        self.assertDictEqual(fields['navbar_title'], {
            'name': 'navbar_title',
            'type': 'rich_text',
            'value': 'a'
        })

        self.assertDictEqual(fields['navbar_subtitle'], {
            'name': 'navbar_subtitle',
            'type': 'rich_text',
            'value': 'b'
        })

        self.assertDictEqual(fields['demo_video_text'], {
            'name': 'demo_video_text',
            'type': 'rich_text',
            'value': 'What is CPDP?'
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'navbar_title',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'text',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
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
            'navbar_title_type': 'rich_text',
            'navbar_title_value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'text',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_create(self):
        data = {
            'fields': [{
                'name': 'navbar_title',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'text',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            }]
        }

        with patch('cms.serializers.SlugPage.objects.create') as mock_func:
            serializer = LandingPageSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'navbar_title_type': 'rich_text',
                    'navbar_title_value': {
                        'blocks': [
                            {
                                'data': {},
                                'depth': 0,
                                'entityRanges': [],
                                'inlineStyleRanges': [],
                                'key': 'abc12',
                                'text': 'text',
                                'type': 'unstyled'
                            }
                        ],
                        'entityMap': {}
                    }
                },
                'slug': 'landing-page',
                'serializer_class': 'LandingPageSerializer'
            })
