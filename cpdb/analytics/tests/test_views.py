import datetime

from django.core.urlresolvers import reverse

from robber import expect
from rest_framework import status
from rest_framework.test import APITestCase
import pytz
from freezegun import freeze_time

from analytics.models import Event


class EventsViewTestCase(APITestCase):

    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_create(self):
        data = {
            'id': 12,
            'title': 'How accurate is the data?'
        }

        url = reverse('api-v2:event-list')
        response = self.client.post(url, {
            'name': 'faq-click',
            'data': data
        }, format='json')
        expect(response.status_code).to.eq(status.HTTP_201_CREATED)

        event = Event.objects.first()
        expect(event.name).to.eq('faq-click')
        expect(event.data).to.eq(data)
        expect(event.created).to.eq(datetime.datetime(2017, 1, 14, 12, 0, 1, tzinfo=pytz.utc))
