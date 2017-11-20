from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import AreaFactory, OfficerFactory, PoliceUnitFactory
from search_terms.models import VIEW_ALL_CTA_TYPE
from search_terms.factories import SearchTermItemFactory


class SearchTermItemsAPITestCase(APITestCase):
    def test_retrieve_area_item(self):
        SearchTermItemFactory(
            slug='police-districts', name='Police Districts', call_to_action_type=VIEW_ALL_CTA_TYPE)
        AreaFactory(name='Kentwood', area_type='police-districts')

        response = self.client.get(reverse('api-v2:search-term-items-detail', kwargs={'pk': 'police-districts'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': 'police-districts',
            'name': 'Police Districts',
            'terms': [
                {
                    'name': 'Kentwood',
                    'link': 'https://beta.cpdb.co/url-mediator/session-builder?police_district=Kentwood'
                }
            ]
        })

    def test_retrieve_officer_rank(self):
        SearchTermItemFactory(
            slug='officer-rank', name='Officer Rank', call_to_action_type=VIEW_ALL_CTA_TYPE)
        OfficerFactory(rank='Independent investigator')

        response = self.client.get(reverse('api-v2:search-term-items-detail', kwargs={'pk': 'officer-rank'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': 'officer-rank',
            'name': 'Officer Rank',
            'terms': [
                {
                    'name': 'Independent investigator',
                    'link': 'https://beta.cpdb.co/url-mediator/session-builder?officer__rank=Independent+investigator'
                }
            ]
        })

    def test_retrieve_officer_unit(self):
        SearchTermItemFactory(
            slug='officer-unit', name='Officer Unit', call_to_action_type=VIEW_ALL_CTA_TYPE)
        PoliceUnitFactory(unit_name='002', description='My awesome unit')

        response = self.client.get(reverse('api-v2:search-term-items-detail', kwargs={'pk': 'officer-unit'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': 'officer-unit',
            'name': 'Officer Unit',
            'terms': [
                {
                    'name': 'My awesome unit',
                    'link': 'https://beta.cpdb.co/url-mediator/session-builder?officer__unit=002'
                }
            ]
        })
