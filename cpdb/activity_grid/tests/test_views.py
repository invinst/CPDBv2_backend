from datetime import datetime

from django.core.urlresolvers import reverse

import pytz
from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from activity_grid.factories import OfficerActivityCardFactory
from data.models import Officer
from data.factories import OfficerFactory, OfficerAllegationFactory
from officers.tests.mixins import OfficerSummaryTestCaseMixin


class ActivityGridViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_list_return_exactly_40_items(self):
        OfficerActivityCardFactory.create_batch(50)
        url = reverse('api-v2:activity-grid-list')
        self.refresh_index()
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(40)

    def test_list_item_content(self):
        officer = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            birth_year=1950,
            race='Asian',
            gender='M'
        )
        OfficerActivityCardFactory(officer=officer)
        OfficerAllegationFactory.create_batch(2, officer=officer, final_finding='SU')
        OfficerAllegationFactory.create_batch(4, officer=officer, final_finding='NS')

        self.refresh_index()
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 1,
                'full_name': 'Jerome Finnigan',
                'visual_token_background_color': '#d4e2f4',
                'complaint_count': 6,
                'sustained_count': 2,
                'birth_year': 1950,
                'race': 'Asian',
                'gender': 'Male',
                'complaint_percentile': None,
                'percentile': {
                    'officer_id': 1,
                    'year': 2016,
                    'percentile_alL_trr': u'0.000',
                    'percentile_civilian': u'77.000',
                    'percentile_internal': u'0.020',
                    'percentile_shooting': u'45.000',
                    'percentile_taser': u'0.100',
                    'percentile_others': u'0.000'
                }
            }
        ])

    def test_list_order(self):
        OfficerActivityCardFactory.create_batch(3, important=True)
        OfficerActivityCardFactory.create_batch(10, last_activity=datetime(2017, 5, 20, tzinfo=pytz.utc))
        OfficerActivityCardFactory.create_batch(10)
        OfficerActivityCardFactory.create_batch(17, last_activity=datetime(2017, 7, 20, tzinfo=pytz.utc))
        url = reverse('api-v2:activity-grid-list')

        self.refresh_index()
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
