from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from cms.serializers import CRPageSerializer


class CRPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        cr_page = Mock()
        cr_page.fields = {
            'document_request_instruction_value': 'a',
            'no_attachment_text_value': 'b',
            'new_document_notification_value': 'c'
        }

        serializer = CRPageSerializer(cr_page)
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
        expect(fields['new_document_notification']).to.eq({
            'name': 'new_document_notification',
            'type': 'rich_text',
            'value': 'c'
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
        cr_page = Mock()
        cr_page.save = Mock()
        cr_page.fields = dict()

        serializer = CRPageSerializer(cr_page, data=data)
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        cr_page.save.assert_called()

        expect(cr_page.fields).to.eq({
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
            serializer = CRPageSerializer(data=data)
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
                'slug': 'cr-page',
                'serializer_class': 'CRPageSerializer'
            })
