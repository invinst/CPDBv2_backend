from django.test import SimpleTestCase

from mock import Mock, patch

from cms.cms_page_descriptors import BaseCMSPageDescriptor
from cms.cms_fields import LinkField
from cms.models import CMSPage


class BaseCMSPageDescriptorTestCase(SimpleTestCase):
    def setUp(self):
        self.mock_cms_page = Mock()

        class CMSPageDescriptor(BaseCMSPageDescriptor):
            slug = 'abc'
            a = LinkField(seed_value='http://abc.xyz')

        self.descriptor_class = CMSPageDescriptor
        self.cms_page_descriptor = CMSPageDescriptor(self.mock_cms_page)

    def test_init_object_with_existing_landing_page(self):
        mock_cms_page = Mock()
        with patch('cms.cms_page_descriptors.CMSPage.objects.get', return_value=mock_cms_page) as mock_function:
            cms_page_descriptor = self.descriptor_class()
            self.assertEqual(cms_page_descriptor.cms_page, mock_cms_page)
            mock_function.assert_called_with(descriptor_class='CMSPageDescriptor')

    def test_init_object_with_non_existing_landing_page(self):
        mock_get = Mock()
        mock_get.side_effect = CMSPage.DoesNotExist
        with patch('cms.cms_page_descriptors.CMSPage.objects.get', new_callable=lambda: mock_get):
            cms_page_descriptor = self.descriptor_class()
            self.assertTrue(cms_page_descriptor.cms_page is None)

    def test_get_fields(self):
        self.assertEqual(
            set([field.name for field in self.cms_page_descriptor.get_fields()]),
            set([
                'a'
            ]))

    def test_get_field_value_from_model(self):
        self.mock_cms_page.fields = {'about_header_type': 'plain_text'}
        self.assertEqual(
            self.cms_page_descriptor.get_field_value_from_model('about_header', 'type'),
            'plain_text')

    def test_seed_data_with_non_existing_cms_page(self):
        mock_get = Mock()
        mock_get.side_effect = CMSPage.DoesNotExist
        with patch('cms.cms_page_descriptors.CMSPage.objects.get', new_callable=lambda: mock_get):
            with patch('cms.cms_page_descriptors.CMSPage.objects.create') as mock_create:
                cms_page_descriptor = self.descriptor_class()
                self.assertTrue(cms_page_descriptor.seed_data() is None)
                mock_create.assert_called_with(slug='abc', fields={
                    'a_type': 'link',
                    'a_value': 'http://abc.xyz'
                    }, descriptor_class='CMSPageDescriptor')

    def test_seed_data_with_existing_cms_page(self):
        self.assertEqual(
            self.cms_page_descriptor.seed_data(),
            None)

    def test_update_cms_page(self):
        self.mock_cms_page.fields = {
            'a_type': 'link',
            'a_value': 'http://abc.xyz'
        }
        self.cms_page_descriptor.update({
            'fields': [
                {
                    'name': 'a',
                    'type': 'link',
                    'value': 'http://def.xyz'
                }
            ]})
        self.assertEqual(self.mock_cms_page.fields['a_value'], 'http://def.xyz')
