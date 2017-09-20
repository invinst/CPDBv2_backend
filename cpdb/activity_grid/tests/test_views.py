from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import OfficerFactory, OfficerAllegationFactory
from activity_grid.factories import OfficerActivityCardFactory
from data.models import Officer


class ActivityGridViewSetTestCase(APITestCase):
    def test_list_return_exactly_40_items(self):
        OfficerActivityCardFactory.create_batch(50)
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(40)

    def test_list_item_content(self):
        officer = OfficerFactory(id=20, first_name='Jerome', last_name='Finnigan')
        OfficerActivityCardFactory(officer=officer)
        OfficerAllegationFactory.create_batch(6, officer=officer)
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
                {
                    'id': 20,
                    'full_name': 'Jerome Finnigan',
                    'visual_token_background_color': '#d4e2f4'
                }
            ])

    def test_list_important_cards(self):
        OfficerActivityCardFactory.create_batch(3, important=True)
        OfficerActivityCardFactory.create_batch(50)
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(40)

        for item in response.data[:3]:
            is_important = Officer.objects.get(pk=item['id']).activity_card.important
            expect(is_important).to.be.true()
