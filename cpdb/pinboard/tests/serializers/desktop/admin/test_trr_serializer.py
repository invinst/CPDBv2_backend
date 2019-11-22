from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from pinboard.serializers.desktop.admin.trr_serializer import TRRSerializer
from trr.factories import TRRFactory, ActionResponseFactory


class TRRSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            trr_1 = TRRFactory(
                id='111',
                trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc)
            )
            ActionResponseFactory(trr=trr_1, force_type='Use Of Force')
            trr_2 = TRRFactory(
                id='222',
                trr_datetime=datetime(2002, 2, 2, tzinfo=pytz.utc)
            )

            expect(TRRSerializer(trr_1).data).to.eq({
                'id': 111,
                'trr_datetime': '2001-01-01',
                'category': 'Use Of Force',
            })

            expect(TRRSerializer(trr_2).data).to.eq({
                'id': 222,
                'trr_datetime': '2002-02-02',
                'category': 'Unknown',
            })
