from django.test import TestCase

from robber import expect

from search_mobile.serializers import TRRSerializer
from trr.factories import TRRFactory


class TRRSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(id=1)

        expect(TRRSerializer(trr).data).to.eq({
            'id': 1,
            'type': 'TRR',
        })
