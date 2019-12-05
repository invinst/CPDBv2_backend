from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from data.factories import AllegationFactory, AllegationCategoryFactory
from pinboard.serializers.desktop.admin.allegation_serializer import AllegationSerializer


class AllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            allegation_1 = AllegationFactory(
                crid='111111',
                most_common_category=AllegationCategoryFactory(category='Use Of Force'),
                incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc),
            )
            allegation_2 = AllegationFactory(
                crid='222222',
                incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc),
            )
            expect(AllegationSerializer(allegation_1).data).to.eq({
                'crid': '111111',
                'category': 'Use Of Force',
                'incident_date': '2001-01-01',
            })
            expect(AllegationSerializer(allegation_2).data).to.eq({
                'crid': '222222',
                'category': 'Unknown',
                'incident_date': '2002-02-02',
            })
