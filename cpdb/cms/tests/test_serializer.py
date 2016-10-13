from django.test import SimpleTestCase

from mock import Mock

from cms.serializers import CMSPageSerializer


class CMSPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        self.descriptor = Mock()
        self.cms_page_serializer = CMSPageSerializer(self.descriptor)

    def test_serialize(self):
        mock_field = Mock()
        mock_field.to_representation = Mock(return_value={'a': 'b'})
        self.descriptor.get_fields = Mock(return_value=[mock_field])
        self.assertEqual(self.cms_page_serializer.data, {'fields': [{'a': 'b'}]})

    def test_update(self):
        data = {
            'fields': {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            }}
        serializer = CMSPageSerializer(self.descriptor, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.update = Mock()
        serializer.save()
        serializer.update.assert_called_with(self.descriptor, data)
