import datetime

from django.test import TestCase

from freezegun import freeze_time
from mock import patch
from robber import expect
import pytz

from data.factories import OfficerFactory
from activity_grid.models import ActivityCard, ActivityPairCard
from twitterbot.post_processors import ActivityGridUpdater
from twitterbot.tests.mixins import RebuildIndexMixin


class ActivityGridUpdaterTestCase(RebuildIndexMixin, TestCase):
    @freeze_time('2017-09-14 12:00:01', tz_offset=0)
    def test_process_single_officer_response(self):
        officer = OfficerFactory()
        updater = ActivityGridUpdater()
        response = {
            'entity': {'id': officer.id},
            'type': 'single_officer'
        }
        self.refresh_index()
        updater.process(response)
        expect(ActivityCard.objects.get(officer=officer).last_activity).to.eq(
            datetime.datetime(2017, 9, 14, 12, 0, 1, tzinfo=pytz.utc))

    @freeze_time('2017-09-14 12:00:01', tz_offset=0)
    def test_process_coaccused_pair_response(self):
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        officer1_doc = {
            'id': officer1.id,
            'full_name': officer1.full_name,
            'percentiles': []
        }
        officer2_doc = {
            'id': officer2.id,
            'full_name': officer2.full_name,
            'percentiles': []
        }
        updater = ActivityGridUpdater()
        response = {
            'officer1': officer1_doc,
            'officer2': officer2_doc,
            'type': 'coaccused_pair'
        }

        self.refresh_index()
        updater.process(response)
        pair_card = ActivityPairCard.objects.get(officer1_id=officer1.id, officer2_id=officer2.id)
        expect(pair_card.last_activity).to.eq(datetime.datetime(2017, 9, 14, 12, 0, 1, tzinfo=pytz.utc))

        updater.process(response)
        expect(ActivityPairCard.objects.count()).to.eq(1)

        updater.process({
            'officer1': officer2_doc,
            'officer2': officer1_doc,
            'type': 'coaccused_pair'
        })
        expect(ActivityPairCard.objects.count()).to.eq(1)

    @patch('twitterbot.post_processors.ActivityCard.objects.get_or_create')
    def test_process_not_recognized_response(self, get_or_create):
        updater = ActivityGridUpdater()
        updater.process(response={'type': 'some_unrecognized_type'})
        expect(get_or_create).not_to.be.called()
