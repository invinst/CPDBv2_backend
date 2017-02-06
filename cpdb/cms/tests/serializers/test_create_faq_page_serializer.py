from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import CreateFAQPageSerializer


class CreateFAQPageSerializerTestCase(SimpleTestCase):
    def test_create_auto_generated_order(self):
        data = {
            'fields': [{
                'name': 'question',
                'type': 'rich_text',
                'value': {'blocks': '', 'entityMap': ''}
            }, {
                'name': 'answer',
                'type': 'rich_text',
                'value': {'blocks': '', 'entityMap': ''}
            }]
        }

        mock_objects = Mock()
        mock_objects.create = Mock()
        mock_objects.count = Mock(return_value=4)
        request = Mock()

        with patch('cms.serializers.FAQPage.objects', mock_objects):
            serializer = CreateFAQPageSerializer(data=data, context={'request': request})
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_objects.create.assert_called_with(fields={
                'question_type': 'rich_text',
                'question_value': {'blocks': '', 'entityMap': ''},
                'answer_type': 'rich_text',
                'answer_value': {'blocks': '', 'entityMap': ''}},
                order=4)

    def test_create_with_order(self):
        data = {
            'fields': [{
                'name': 'question',
                'type': 'rich_text',
                'value': {'blocks': '', 'entityMap': ''}
            }, {
                'name': 'answer',
                'type': 'rich_text',
                'value': {'blocks': '', 'entityMap': ''}
            }],
            'meta': {
                'order': 1
            }
        }

        request = Mock()

        with patch('cms.serializers.FAQPage.objects.create') as mock_func:
            serializer = CreateFAQPageSerializer(data=data, context={'request': request})
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(fields={
                'question_type': 'rich_text',
                'question_value': {'blocks': '', 'entityMap': ''},
                'answer_type': 'rich_text',
                'answer_value': {'blocks': '', 'entityMap': ''}},
                order=1)
