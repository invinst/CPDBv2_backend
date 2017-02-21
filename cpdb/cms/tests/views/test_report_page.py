from django.core.urlresolvers import reverse

from mock import patch
from robber import expect

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from data.factories import OfficerFactory
from cms.serializers import ReportPageSerializer
from cms.models import ReportPage


class ReportPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            self.officer_1 = OfficerFactory(gender='M')
            self.officer_2 = OfficerFactory()

            serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data(
                title='a', excerpt=['b', 'c'], publication='d',
                publish_date='2016-10-25', author='e', article_link='f'))
            serializer.is_valid()
            serializer.save()
            serializer.instance.officers.add(self.officer_1)

            serializer2 = ReportPageSerializer(data=ReportPageSerializer().fake_data())
            serializer2.is_valid()
            serializer2.save()
        self.maxDiff = None

    def fields_list_to_dict(self, fields):
        return {
            field['name']: field
            for field in fields
        }

    def test_retrieve_report_page(self):
        report = ReportPage.objects.first()
        url = reverse('api-v2:report-detail', kwargs={'pk': report.id})

        response = self.client.get(url)
        fields = self.fields_list_to_dict(response.data['fields'])

        expect(response.data['id']).to.eq(report.id)
        expect(fields['author']).to.eq({
            'name': 'author',
            'type': 'string',
            'value': 'e'
        })
        expect(fields['publication']).to.eq({
            'name': 'publication',
            'type': 'string',
            'value': 'd'
        })
        expect(fields['publish_date']).to.eq({
            'name': 'publish_date',
            'type': 'date',
            'value': '2016-10-25'
        })
        expect(fields['excerpt']).to.eq({
            'name': 'excerpt',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'b',
                        'type': 'unstyled'
                    },
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'c',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        expect(fields['title']).to.eq({
            'name': 'title',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'a',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        expect(fields['article_link']).to.eq({
            'name': 'article_link',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'f',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

        expect(len(fields['officers']['value'])).to.eq(1)
        expect(fields['officers']).to.eq({
            'name': 'officers',
            'type': 'officers_list',
            'value': [{
                'id': self.officer_1.id,
                'allegation_count': self.officer_1.allegation_count,
                'full_name': self.officer_1.full_name,
                'v1_url': self.officer_1.v1_url,
                'race': self.officer_1.race,
                'gender': 'Male'
            }]
        })

    def test_list_report_page(self):
        url = reverse('api-v2:report-list')

        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        [report1, report2] = ReportPage.objects.all().order_by('created')
        actual_data = dict(response.data)

        expect(actual_data['results'][0]['id']).to.eq(report2.id)
        expect(actual_data['results'][1]['id']).to.eq(report1.id)
        fields = self.fields_list_to_dict(actual_data['results'][1]['fields'])

        expect(len(fields.keys())).to.eq(7)
        expect(actual_data['count']).to.eq(2)
        expect(actual_data['next']).to.eq(None)
        expect(actual_data['previous']).to.eq(None)

        expect(fields['author']).to.eq({
            'name': 'author',
            'type': 'string',
            'value': 'e'
        })
        expect(fields['publication']).to.eq({
            'name': 'publication',
            'type': 'string',
            'value': 'd'
        })
        expect(fields['publish_date']).to.eq({
            'name': 'publish_date',
            'type': 'date',
            'value': '2016-10-25'
        })
        expect(fields['excerpt']).to.eq({
            'name': 'excerpt',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'b',
                        'type': 'unstyled'
                    },
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'c',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        expect(fields['title']).to.eq({
            'name': 'title',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'a',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        expect(fields['article_link']).to.eq({
            'name': 'article_link',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'f',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_update_report_page_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'title',
                'type': 'rich_text',
                'value': 'new title'
            }
        ]}, format='json')
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': {
                'title': 'Value must be in raw content state format'
            }
        })

    def test_update_report_page(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'publication',
                'type': 'string',
                'value': 'new york times'
            }
        ]}, format='json')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(len(response.data['fields'])).to.eq(7)
        response_data = self.fields_list_to_dict(response.data['fields'])
        expect(response_data['publication']['value']).to.eq('new york times')
        report_page.refresh_from_db()
        expect(report_page.fields['publication_value']).to.eq('new york times')

    def patch_first_report(self, data):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return report_page, self.client.patch(url, data, format='json')

    def test_update_report_page_with_officer(self):
        report_page, response = self.patch_first_report({'fields': [
            {
                'name': 'officers',
                'type': 'officers_list',
                'value': [{
                    'id': self.officer_2.pk
                }]
            }
        ]})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        response_data = self.fields_list_to_dict(response.data['fields'])
        expect(response_data['officers']['value'][0]['id']).to.eq(self.officer_2.pk)

        report_page.refresh_from_db()
        expect(report_page.officers.count()).to.eq(1)
        expect(report_page.officers.all().values_list('id', flat=True)[0]).to.eq(self.officer_2.pk)

    def test_update_report_page_with_non_existant_officer(self):
        _, response = self.patch_first_report({'fields': [
            {
                'name': 'officers',
                'type': 'officers_list',
                'value': [{
                    'id': 456
                }]
            }
        ]})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': {
                'officers': 'Officer does not exist'
            }
        })

    def test_update_report_page_with_incorrect_officers_format(self):
        _, response = self.patch_first_report({'fields': [
            {
                'name': 'officers',
                'type': 'officers_list',
                'value': [123]
            }
        ]})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': {
                'officers': 'Incorrect type. Expected officer pk'
            }
        })

    def test_add_report_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('api-v2:report-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'title',
                'type': 'rich_text',
                'value': 'a'
            }, {
                'name': 'excerpt',
                'type': 'rich_text',
                'value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            }, {
                'name': 'publication',
                'type': 'string',
                'value': 'ccc'
            }, {
                'name': 'publish_date',
                'type': 'date',
                'value': '1900-01-01'
            }, {
                'name': 'author',
                'type': 'string',
                'value': 'ddd'
            }]
        }, format='json')
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': {
                'title': 'Value must be in raw content state format'
            }
        })

    def test_add_report(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('api-v2:report-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'title',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }, {
                'name': 'excerpt',
                'type': 'rich_text',
                'value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            }, {
                'name': 'publication',
                'type': 'string',
                'value': 'ccc'
            }, {
                'name': 'publish_date',
                'type': 'date',
                'value': '1900-01-01'
            }, {
                'name': 'author',
                'type': 'string',
                'value': 'ddd'
            }, {
                'name': 'officers',
                'value': [{'id': self.officer_1.id}]
            }]
        }, format='json')
        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        created_report = ReportPage.objects.last()
        expect(created_report.fields).to.eq({
            'title_value': {
                'blocks': 'a',
                'entityMap': 'b'
            },
            'title_type': 'rich_text',
            'excerpt_value': {
                'blocks': 'c',
                'entityMap': 'd'
            },
            'excerpt_type': 'rich_text',
            'publication_value': 'ccc',
            'publication_type': 'string',
            'publish_date_value': '1900-01-01',
            'publish_date_type': 'date',
            'author_value': 'ddd',
            'author_type': 'string'
        })
        expect(created_report.officers.count()).to.eq(1)
        expect(created_report.officers.all()[0].id).to.eq(self.officer_1.id)
