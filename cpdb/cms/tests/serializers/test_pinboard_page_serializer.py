from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from cms.serializers import PinboardPageSerializer


class PinboardPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        pinboard_page = Mock()
        pinboard_page.fields = {
            'empty_pinboard_title_value': 'Get started',
            'empty_pinboard_description_value': 'Use search to find officers and individual complaint records'
        }

        serializer = PinboardPageSerializer(pinboard_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }
        expected_title = {
            'name': 'empty_pinboard_title',
            'type': 'rich_text',
            'value': 'Get started'
        }
        expected_description = {
            'name': 'empty_pinboard_description',
            'type': 'rich_text',
            'value': 'Use search to find officers and individual complaint records'
        }
        expect(fields['empty_pinboard_title']).to.eq(expected_title)
        expect(fields['empty_pinboard_description']).to.eq(expected_description)

    def test_update(self):
        data = {
            'fields': [{
                'name': 'empty_pinboard_title',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc123',
                            'text': 'Getting started',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            }]
        }
        pinboard_page = Mock()
        pinboard_page.save = Mock()
        pinboard_page.fields = dict()

        serializer = PinboardPageSerializer(pinboard_page, data=data)
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        expect(pinboard_page.save).to.be.called()

        expected_result = {
            'empty_pinboard_title_type': 'rich_text',
            'empty_pinboard_title_value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc123',
                        'text': 'Getting started',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        }
        expect(pinboard_page.fields).to.eq(expected_result)

    def test_create(self):
        data = {
            'fields': [{
                'name': 'empty_pinboard_title',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc123',
                            'text': 'Get started',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            }]
        }

        with patch('cms.serializers.SlugPage.objects.create') as mock_func:
            serializer = PinboardPageSerializer(data=data)
            expect(serializer.is_valid()).to.be.true()
            serializer.save()
            expect(mock_func).to.be.called_with(**{
                'fields': {
                    'empty_pinboard_title_type': 'rich_text',
                    'empty_pinboard_title_value': {
                        'blocks': [
                            {
                                'data': {},
                                'depth': 0,
                                'entityRanges': [],
                                'inlineStyleRanges': [],
                                'key': 'abc123',
                                'text': 'Get started',
                                'type': 'unstyled'
                            }
                        ],
                        'entityMap': {}
                    }
                },
                'slug': 'pinboard-page',
                'serializer_class': 'PinboardPageSerializer'
            })
