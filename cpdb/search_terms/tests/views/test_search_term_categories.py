from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from search_terms.models import VIEW_ALL_CTA_TYPE, PLAIN_TEXT_CTA_TYPE, LINK_CTA_TYPE
from search_terms.factories import SearchTermCategoryFactory, SearchTermItemFactory


class SearchTermCategoriesAPITestCase(APITestCase):
    def test_list(self):
        category1 = SearchTermCategoryFactory(name='my category 1')
        SearchTermItemFactory(
            category=category1, slug='item_1', name='item 1',
            description='my item 1', call_to_action_type=VIEW_ALL_CTA_TYPE,
            link='/url-mediator/session-builder?my_query_key=123')
        category2 = SearchTermCategoryFactory(name='my category 2')
        SearchTermItemFactory(
            category=category2, slug='item_2', name='item 2',
            description='my item 2', call_to_action_type=PLAIN_TEXT_CTA_TYPE,
            link='/url-mediator/session-builder?my_query_key=456')
        SearchTermItemFactory(
            category=category2, slug='item_3', name='item 3',
            description='my item 3', call_to_action_type=LINK_CTA_TYPE,
            link='/url-mediator/session-builder?my_query_key=789')

        response = self.client.get(reverse('api-v2:search-term-categories-list'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq([
            {
                'name': 'my category 1',
                'items': [
                    {
                        'id': 'item_1',
                        'name': 'item 1',
                        'description': 'my item 1',
                        'call_to_action_type': 'view_all',
                        'link': 'http://cpdb.lvh.me/url-mediator/session-builder?my_query_key=123'
                    }
                ]
            },
            {
                'name': 'my category 2',
                'items': [
                    {
                        'id': 'item_2',
                        'name': 'item 2',
                        'description': 'my item 2',
                        'call_to_action_type': 'plain_text',
                        'link': 'http://cpdb.lvh.me/url-mediator/session-builder?my_query_key=456'
                    },
                    {
                        'id': 'item_3',
                        'name': 'item 3',
                        'description': 'my item 3',
                        'call_to_action_type': 'link',
                        'link': 'http://cpdb.lvh.me/url-mediator/session-builder?my_query_key=789'
                    }
                ]
            }
        ])
