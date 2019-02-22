from django.test import TestCase

from robber import expect

from analytics.models import Event
from analytics import constants


class EventTestCase(TestCase):
    def test_create_attachment_download_events(self):
        Event.objects.create_attachment_download_events([1, 2])

        events = Event.objects.all()

        expect(events).to.have.length(2)
        expect(events[0].name).to.eq(constants.EVT_ATTACHMENT_DOWNLOAD)
        expect(events[0].data['id']).to.eq(1)
        expect(events[1].name).to.eq(constants.EVT_ATTACHMENT_DOWNLOAD)
        expect(events[1].data['id']).to.eq(2)

    def test_get_attachment_download_events(self):
        Event.objects.create(name='dummy', data={'id': 1})
        Event.objects.create_attachment_download_events([1, 2])

        events = Event.objects.get_attachment_download_events()
        expect(events).to.have.length(2)
        expect(events[0].name).to.eq(constants.EVT_ATTACHMENT_DOWNLOAD)
        expect(events[0].data['id']).to.eq(1)
        expect(events[1].name).to.eq(constants.EVT_ATTACHMENT_DOWNLOAD)
        expect(events[1].data['id']).to.eq(2)

        events = Event.objects.get_attachment_download_events([1])
        expect(events).to.have.length(1)
        expect(events[0].name).to.eq(constants.EVT_ATTACHMENT_DOWNLOAD)
        expect(events[0].data['id']).to.eq(1)

    def test_attachment_id(self):
        event1 = Event.objects.create(name='dummy', data={'id': 1})
        event2 = Event.objects.create(name=constants.EVT_ATTACHMENT_DOWNLOAD, data={})
        event3 = Event.objects.create(name=constants.EVT_ATTACHMENT_DOWNLOAD, data={'id': 2})

        expect(event1.attachment_id).to.eq(None)
        expect(event2.attachment_id).to.eq(None)
        expect(event3.attachment_id).to.eq(2)
