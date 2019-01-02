from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from cms.serializers import TRRPageSerializer


class TRRPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        trr_page = Mock()
        trr_page.fields = {
            'document_request_instruction_value': 'a',
            'no_attachment_text_value': 'b'
        }

        serializer = TRRPageSerializer(trr_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }
        expect(fields['document_request_instruction']).to.eq({
            'name': 'document_request_instruction',
            'type': 'rich_text',
            'value': 'a'
        })
        expect(fields['no_attachment_text']).to.eq({
            'name': 'no_attachment_text',
            'type': 'rich_text',
            'value': 'b'
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'document_request_instruction',
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
        trr_page = Mock()
        trr_page.save = Mock()
        trr_page.fields = dict()

        serializer = TRRPageSerializer(trr_page, data=data)
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        trr_page.save.assert_called()

        expect(trr_page.fields).to.eq({
            'document_request_instruction_type': 'rich_text',
            'document_request_instruction_value': {
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
                'name': 'document_request_instruction',
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
            serializer = TRRPageSerializer(data=data)
            expect(serializer.is_valid()).to.be.true()
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'document_request_instruction_type': 'rich_text',
                    'document_request_instruction_value': {
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
                'slug': 'trr-page',
                'serializer_class': 'TRRPageSerializer'
            })
