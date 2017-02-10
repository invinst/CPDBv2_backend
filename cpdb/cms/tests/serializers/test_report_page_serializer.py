from django.test import SimpleTestCase

from mock import Mock, patch

from cms.serializers import ReportPageSerializer


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
        report_page.officers = [{
            'id': 1,
            'allegation_count': 1,
            'full_name': 'Mr. Foo',
            'v1_url': 'v1_url',
            'race': 'race',
            'gender_display': 'Male'
        }]
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

        self.assertDictEqual(fields['officers'], {
            'name': 'officers',
            'type': 'officers_list',
            'value': [{
                'id': 1,
                'allegation_count': 1,
                'full_name': 'Mr. Foo',
                'v1_url': 'v1_url',
                'race': 'race',
                'gender': 'Male'
            }]
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
