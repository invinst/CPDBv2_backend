from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import FAQPageSerializer


class FAQPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        faq_page = Mock()
        faq_page.fields = {
            'question_value': 'a',
            'answer_value': 'b',
        }
        faq_page.order = 1

        serializer = FAQPageSerializer(faq_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }

        self.assertDictEqual(serializer.data['meta'], {'order': 1})
        self.assertDictEqual(fields['question'], {
            'name': 'question',
            'type': 'rich_text',
            'value': 'a'
        })

        self.assertDictEqual(fields['answer'], {
            'name': 'answer',
            'type': 'rich_text',
            'value': 'b'
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'question',
                'type': 'rich_text',
                'value': {'blocks': '', 'entityMap': ''}
            }],
            'meta': {
                'order': 1
            }
        }
        faq_page = Mock()
        faq_page.save = Mock()
        faq_page.fields = dict()
        faq_page.order = 0

        serializer = FAQPageSerializer(faq_page, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        faq_page.save.assert_called()
        self.assertDictEqual(faq_page.fields, {
            'question_type': 'rich_text',
            'question_value': {'blocks': '', 'entityMap': ''}
        })
        self.assertEqual(faq_page.order, 1)

    def test_create(self):
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

        with patch('cms.serializers.FAQPage.objects.create') as mock_func:
            serializer = FAQPageSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(fields={
                'question_type': 'rich_text',
                'question_value': {'blocks': '', 'entityMap': ''},
                'answer_type': 'rich_text',
                'answer_value': {'blocks': '', 'entityMap': ''}},
                order=1)

    def test_bulk_update(self):
        object1 = Mock()
        object1.id = 1
        object1.order = 1
        object1.fields = dict()
        object2 = Mock()
        object2.id = 2
        object2.order = 2
        object2.fields = dict()
        object3 = Mock()
        object3.id = 3
        object3.order = 3
        object3.fields = dict()
        objects = [object1, object2, object3]
        data = [{
            'id': 1,
            'meta': {'order': 2}
        }, {
            'id': 2,
            'meta': {'order': 1}
        }]

        serializer = FAQPageSerializer(objects, many=True, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(serializer.data[0]['id'], 1)
        self.assertDictEqual(serializer.data[0]['meta'], {'order': 2})
        self.assertEqual(serializer.data[1]['id'], 2)
        self.assertDictEqual(serializer.data[1]['meta'], {'order': 1})
