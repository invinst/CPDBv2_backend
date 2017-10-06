import datetime

from django.test import TestCase

from freezegun import freeze_time
from mock import patch
from robber import expect
import pytz

from data.factories import OfficerFactory
from activity_grid.models import ActivityCard
from twitterbot.models import TYPE_SINGLE_OFFICER
from twitterbot.post_processors import ActivityGridUpdater


class ActivityGridUpdaterTestCase(TestCase):
    @freeze_time('2017-09-14 12:00:01', tz_offset=0)
    def test_process_single_officer_response(self):
        officer = OfficerFactory()
        updater = ActivityGridUpdater()
        response = {
            'entity': officer,
            'type': TYPE_SINGLE_OFFICER
        }
        updater.process(response)
        expect(ActivityCard.objects.get(officer=officer).last_activity).to.eq(
            datetime.datetime(2017, 9, 14, 12, 0, 1, tzinfo=pytz.utc))

    @patch('twitterbot.post_processors.ActivityCard.objects.get_or_create')
    def test_process_not_recognized_response(self, get_or_create):
        updater = ActivityGridUpdater()
        updater.process(response={'type': 'some_unrecognized_type'})
        expect(get_or_create).not_to.be.called()
