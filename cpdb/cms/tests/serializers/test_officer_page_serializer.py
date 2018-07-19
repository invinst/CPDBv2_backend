from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from cms.serializers import OfficerPageSerializer


class OfficerPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        officer_page = Mock()
        officer_page.fields = {
            'triangle_description_value': 'a',
            'triangle_sub_description_value': 'b'
        }

        serializer = OfficerPageSerializer(officer_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }
        expected_description = {
            'name': 'triangle_description',
            'type': 'rich_text',
            'value': 'a'
        }
        expected_sub_description = {
            'name': 'triangle_sub_description',
            'type': 'rich_text',
            'value': 'b'
        }
        expect(fields['triangle_description']).to.eq(expected_description)
        expect(fields['triangle_sub_description']).to.eq(expected_sub_description)

    def test_update(self):
        data = {
            'fields': [{
                'name': 'triangle_description',
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

        serializer = OfficerPageSerializer(landing_page, data=data)
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        landing_page.save.assert_called()

        expected_result = {
            'triangle_description_type': 'rich_text',
            'triangle_description_value': {
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
        }
        expect(landing_page.fields).to.eq(expected_result)

    def test_create(self):
        data = {
            'fields': [{
                'name': 'triangle_description',
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
            serializer = OfficerPageSerializer(data=data)
            expect(serializer.is_valid()).to.be.true()
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'triangle_description_type': 'rich_text',
                    'triangle_description_value': {
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
                'slug': 'officer-page',
                'serializer_class': 'OfficerPageSerializer'
            })
