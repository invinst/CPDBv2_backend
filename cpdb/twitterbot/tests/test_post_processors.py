import datetime

from django.test import TestCase

from freezegun import freeze_time
from mock import patch
from robber import expect
import pytz

from data.factories import OfficerFactory
from activity_grid.models import ActivityCard, ActivityPairCard
from twitterbot.post_processors import ActivityGridUpdater


class ActivityGridUpdaterTestCase(TestCase):
    @freeze_time('2017-09-14 12:00:01', tz_offset=0)
    def test_process_single_officer_response(self):
        officer = OfficerFactory()
        updater = ActivityGridUpdater()
        response = {
            'entity': officer,
            'type': 'single_officer'
        }
        updater.process(response)
        expect(ActivityCard.objects.get(officer=officer).last_activity).to.eq(
            datetime.datetime(2017, 9, 14, 12, 0, 1, tzinfo=pytz.utc))

    @freeze_time('2017-09-14 12:00:01', tz_offset=0)
    def test_process_coaccused_pair_response(self):
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        updater = ActivityGridUpdater()
        response = {
            'officer1': officer1,
            'officer2': officer2,
            'type': 'coaccused_pair'
        }

        updater.process(response)
        pair_card = ActivityPairCard.objects.get(officer1=officer1, officer2=officer2)
        expect(pair_card.last_activity).to.eq(datetime.datetime(2017, 9, 14, 12, 0, 1, tzinfo=pytz.utc))

        updater.process(response)
        expect(ActivityPairCard.objects.count()).to.eq(1)

        updater.process({
            'officer1': officer2,
            'officer2': officer1,
            'type': 'coaccused_pair'
        })
        expect(ActivityPairCard.objects.count()).to.eq(1)

    @patch('twitterbot.post_processors.ActivityCard.objects.get_or_create')
    def test_process_not_recognized_response(self, get_or_create):
        updater = ActivityGridUpdater()
        updater.process(response={'type': 'some_unrecognized_type'})
        expect(get_or_create).not_to.be.called()
