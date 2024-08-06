from django.test import TestCase

from robber import expect

from search_mobile.serializers import TRRRecentSerializer
from trr.factories import TRRFactory


class TRRRecentSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(id=1)

        expect(TRRRecentSerializer(trr).data).to.eq({
            'id': 1,
            'type': 'TRR',
        })
