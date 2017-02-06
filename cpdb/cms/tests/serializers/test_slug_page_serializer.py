from django.test import SimpleTestCase

from mock import Mock

from cms.serializers import SlugPageSerializer
from cms.fields import StringField


class SlugPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        self.page_model = Mock()
        self.page_model.objects = Mock()
        self.page_model.objects.create = Mock()

        class PageSerializer(SlugPageSerializer):
            a = StringField(source='fields')

            class Meta:
                model = self.page_model
                slug = 'page'

        self.serializer_class = PageSerializer

    def test_create(self):
        serializer = self.serializer_class(data={'fields': [{'name': 'a', 'type': 'string', 'value': 'c'}]})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.page_model.objects.create.assert_called_with(
            fields={'a_type': 'string', 'a_value': 'c'}, slug='page',
            serializer_class='PageSerializer')
