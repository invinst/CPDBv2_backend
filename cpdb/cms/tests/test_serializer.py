from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import (
    BaseCMSPageSerializer, LandingPageSerializer, ReportPageSerializer,
    SlugPageSerializer, IdPageSerializer)
from cms.fields import StringField
from cms.randomizers import RANDOMIZER_STRATEGIES


class BaseCMSPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        self.page_model = Mock()
        self.page_model.objects = Mock()
        self.page_model.objects.create = Mock()

        class CMSPageSerializer(BaseCMSPageSerializer):
            a = StringField()

            class Meta:
                model = self.page_model

        self.serializer_class = CMSPageSerializer

    def test_serialize(self):
        page = Mock()
        page.fields = {
            'a_value': 'b'
        }
        serializer = self.serializer_class(page)
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'b'
        })

    def test_update(self):
        page = Mock()
        page.fields = {
            'a_value': 'b'
        }
        page.save = Mock()
        serializer = self.serializer_class(page, data={'fields': [{'name': 'a', 'type': 'string', 'value': 'c'}]})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'c'
        })
        page.save.assert_called()

    def test_create(self):
        serializer = self.serializer_class(data={'fields': [{'name': 'a', 'type': 'string', 'value': 'c'}]})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.page_model.objects.create.assert_called_with(fields={'a_type': 'string', 'a_value': 'c'})

    def test_fake_data(self):
        self.assertDictEqual(self.serializer_class().fake_data(a='b'), {'fields': [{
            'name': 'a',
            'type': 'string',
            'value': 'b'
        }]})


class SlugPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        self.page_model = Mock()
        self.page_model.objects = Mock()
        self.page_model.objects.create = Mock()

        class PageSerializer(SlugPageSerializer):
            a = StringField()

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


class IdPageSerializerTestCase(SimpleTestCase):
    def setUp(self):
        class PageSerializer(IdPageSerializer):
            a = StringField()

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


class LandingPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        landing_page = Mock()
        landing_page.fields = {
            'reporting_header_value': 'a',
            'reporting_randomizer_pool_size': 10,
            'reporting_randomizer_selected_strategy_id': 1,
            'faq_header_value': 'b',
            'faq_randomizer_pool_size': 10,
            'faq_randomizer_selected_strategy_id': 1,
            'vftg_date_value': 'c',
            'vftg_link_value': 'd',
            'vftg_content_value': 'e',
            'collaborate_header_value': 'f',
            'collaborate_content_value': 'g',
            'about_header_value': 'h',
            'about_content_value': 'i'
        }
        with patch('cms.serializers.randomize', return_value=[]):
            serializer = LandingPageSerializer(landing_page)
            fields = {
                field['name']: field
                for field in serializer.data['fields']
            }

        self.assertDictEqual(fields['reporting_header'], {
            'name': 'reporting_header',
            'type': 'rich_text',
            'value': 'a'
        })

        self.assertDictEqual(fields['reporting_randomizer'], {
            'name': 'reporting_randomizer',
            'type': 'randomizer',
            'value': {
                'poolSize': 10,
                'selectedStrategyId': 1,
                'strategies': RANDOMIZER_STRATEGIES
            }
        })

        self.assertDictEqual(fields['faq_header'], {
            'name': 'faq_header',
            'type': 'rich_text',
            'value': 'b'
        })

        self.assertDictEqual(fields['faq_randomizer'], {
            'name': 'faq_randomizer',
            'type': 'randomizer',
            'value': {
                'poolSize': 10,
                'selectedStrategyId': 1,
                'strategies': RANDOMIZER_STRATEGIES
            }
        })

        self.assertDictEqual(fields['vftg_date'], {
            'name': 'vftg_date',
            'type': 'date',
            'value': 'c'
        })

        self.assertDictEqual(fields['vftg_link'], {
            'name': 'vftg_link',
            'type': 'link',
            'value': 'd'
        })

        self.assertDictEqual(fields['vftg_content'], {
            'name': 'vftg_content',
            'type': 'rich_text',
            'value': 'e'
        })

        self.assertDictEqual(fields['collaborate_header'], {
            'name': 'collaborate_header',
            'type': 'rich_text',
            'value': 'f'
        })

        self.assertDictEqual(fields['collaborate_content'], {
            'name': 'collaborate_content',
            'type': 'rich_text',
            'value': 'g'
        })

        self.assertDictEqual(fields['about_header'], {
            'name': 'about_header',
            'type': 'rich_text',
            'value': 'h'
        })

        self.assertDictEqual(fields['about_content'], {
            'name': 'about_content',
            'type': 'rich_text',
            'value': 'i'
        })

        self.assertDictEqual(fields['reports'], {
            'name': 'reports',
            'type': 'randomized_list',
            'value': []
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            }]
        }
        landing_page = Mock()
        landing_page.save = Mock()
        landing_page.fields = dict()

        serializer = LandingPageSerializer(landing_page, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        landing_page.save.assert_called()
        self.assertDictEqual(landing_page.fields, {
            'vftg_link_type': 'link',
            'vftg_link_value': 'http://abc.xyz'
        })

    def test_create(self):
        data = {
            'fields': [{
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            }]
        }

        with patch('cms.serializers.SlugPage.objects.create') as mock_func:
            serializer = LandingPageSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'vftg_link_type': 'link',
                    'vftg_link_value': 'http://abc.xyz'
                },
                'slug': 'landing-page',
                'serializer_class': 'LandingPageSerializer'
            })


class ReportPageSerializerTestCase(SimpleTestCase):
    def test_serialize(self):
        report_page = Mock()
        report_page.fields = {
            'title_value': 'a',
            'excerpt_value': 'b',
            'publication_value': 'c',
            'publish_date_value': '2016-10-25',
            'author_value': 'd'
        }
        serializer = ReportPageSerializer(report_page)
        fields = {
            field['name']: field
            for field in serializer.data['fields']
        }

        self.assertDictEqual(fields['title'], {
            'name': 'title',
            'type': 'rich_text',
            'value': 'a'
        })

        self.assertDictEqual(fields['excerpt'], {
            'name': 'excerpt',
            'type': 'rich_text',
            'value': 'b'
        })

        self.assertDictEqual(fields['publication'], {
            'name': 'publication',
            'type': 'string',
            'value': 'c'
        })

        self.assertDictEqual(fields['publish_date'], {
            'name': 'publish_date',
            'type': 'date',
            'value': '2016-10-25'
        })

        self.assertDictEqual(fields['author'], {
            'name': 'author',
            'type': 'string',
            'value': 'd'
        })

    def test_update(self):
        data = {
            'fields': [{
                'name': 'author',
                'type': 'string',
                'value': 'Carl Jung'
            }]
        }
        report_page = Mock()
        report_page.save = Mock()
        report_page.fields = dict()

        serializer = ReportPageSerializer(report_page, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        report_page.save.assert_called()
        self.assertDictEqual(report_page.fields, {
            'author_type': 'string',
            'author_value': 'Carl Jung'
        })

    def test_create(self):
        data = {
            'fields': [{
                'name': 'publication',
                'type': 'string',
                'value': 'New York Times'
            }]
        }

        with patch('cms.serializers.ReportPage.objects.create') as mock_func:
            serializer = ReportPageSerializer(data=data)
            self.assertTrue(serializer.is_valid())
            serializer.save()
            mock_func.assert_called_with(**{
                'fields': {
                    'publication_type': 'string',
                    'publication_value': 'New York Times'
                }
            })
