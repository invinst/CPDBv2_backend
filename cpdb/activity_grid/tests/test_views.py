from datetime import datetime, date
import pytz

from django.core.urlresolvers import reverse

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
            gender='M',
            appointed_date=datetime(2011, 1, 1)
        )
        OfficerActivityCardFactory(officer=officer)
        OfficerAllegationFactory(
            officer=officer, final_finding='SU',
            start_date=date(2014, 1, 1),
            allegation__incident_date=datetime(2014, 1, 1))
        OfficerAllegationFactory(
            officer=officer, final_finding='SU',
            allegation__incident_date=datetime(2016, 1, 1),
            start_date=date(2016, 1, 1)
        )
        OfficerAllegationFactory.create_batch(
            4,
            officer=officer,
            final_finding='NS',
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2015, 2, 20)
        )

        self.refresh_index()
        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 1,
                'full_name': 'Jerome Finnigan',
                'complaint_count': 6,
                'sustained_count': 2,
                'birth_year': 1950,
                'complaint_percentile': '0.000',
                'race': 'Asian',
                'gender': 'Male',
                'percentile': {
                    'id': 1,
                    'year': 2016,
                    'percentile_trr': '0.000',
                    'percentile_allegation': '0.000',
                    'percentile_allegation_internal': '0.000',
                    'percentile_allegation_civilian': '0.000'

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
