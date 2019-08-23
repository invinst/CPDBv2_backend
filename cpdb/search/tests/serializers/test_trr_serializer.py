from datetime import datetime

from django.test import TestCase

from robber import expect
import pytz

from search.serializers import TRRSerializer
from trr.factories import TRRFactory, ActionResponseFactory


class TRRSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(id=1, trr_datetime=datetime(2007, 1, 1, tzinfo=pytz.utc))
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Taser', action_sub_category='5.1')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

        expect(TRRSerializer(trr).data).to.eq({
            'id': 1,
            'trr_datetime': '2007-01-01',
            'force_type': 'Impact Weapon',
            'type': 'TRR',
        })
