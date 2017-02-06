from django.test import SimpleTestCase

from mock import Mock

from cms.serializers import IdPageSerializer
from cms.fields import StringField


class IdPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        self.page_model = Mock()
        self.page_model.objects = Mock()
        self.page_model.objects.create = Mock()

        class PageSerializer(IdPageSerializer):
            a = StringField(source='fields')

            class Meta:
                model = self.page_model

        self.serializer_class = PageSerializer

    def test_serialize(self):
        page = Mock()
        page.fields = {
            'a_value': 'b'
        }
        page.id = 1
        serializer = self.serializer_class(page)
        self.assertEqual(serializer.data['id'], 1)
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'b'
        })
