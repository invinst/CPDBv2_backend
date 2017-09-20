from datetime import datetime

from django.core.urlresolvers import reverse

import pytz
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

    def test_list_order(self):
        OfficerActivityCardFactory.create_batch(3, important=True)
        OfficerActivityCardFactory.create_batch(10, last_activity=datetime(2017, 5, 20, tzinfo=pytz.utc))
        OfficerActivityCardFactory.create_batch(10)
        OfficerActivityCardFactory.create_batch(17, last_activity=datetime(2017, 7, 20, tzinfo=pytz.utc))
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(40)

        for item in response.data[:3]:
            is_important = Officer.objects.get(pk=item['id']).activity_card.important
            expect(is_important).to.be.true()

        for item in response.data[3:20]:
            activity_card = Officer.objects.get(pk=item['id']).activity_card
            expect(activity_card.last_activity).to.eq(datetime(2017, 7, 20, tzinfo=pytz.utc))

        for item in response.data[20:30]:
            activity_card = Officer.objects.get(pk=item['id']).activity_card
            expect(activity_card.last_activity).to.eq(datetime(2017, 5, 20, tzinfo=pytz.utc))
