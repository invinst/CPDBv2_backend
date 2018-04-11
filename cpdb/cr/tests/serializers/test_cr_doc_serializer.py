from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from cr.serializers.cr_doc_serializer import CRDocSerializer
from data.factories import (
    AllegationFactory, AreaFactory
)


class CRDocSerializerTestCase(TestCase):
    def test_get_point(self):
        allegation = AllegationFactory(point=None)
        result = CRDocSerializer(allegation).data
        expect(result['point']).to.eq(None)

        allegation = AllegationFactory(point=Point(1.0, 1.0))
        result = CRDocSerializer(allegation).data
        expect(result['point']).to.eq({'lon': 1.0, 'lat': 1.0})

    def test_get_beat(self):
        allegation = AllegationFactory(beat=None)
        result = CRDocSerializer(allegation).data
        expect(result['beat']).to.eq(None)

        allegation = AllegationFactory(beat=AreaFactory(name='23'))
        result = CRDocSerializer(allegation).data
        expect(result['beat']).to.eq('23')
