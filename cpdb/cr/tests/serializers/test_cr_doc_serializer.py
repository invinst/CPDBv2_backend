from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from cr.serializers.cr_doc_serializer import CRDocSerializer, InvestigatorAllegationSerializer
from data.factories import (
    AllegationFactory, AreaFactory, InvestigatorAllegationFactory, OfficerFactory
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


class InvestigatorAllegationSerializerTestCase(TestCase):
    def test_get_full_name(self):
        investigator_allegation = InvestigatorAllegationFactory(
            investigator__officer=None,
            investigator__first_name='German',
            investigator__last_name='Lauren'
        )

        result = InvestigatorAllegationSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('German Lauren')
        expect(result['abbr_name']).to.eq('G. Lauren')

        investigator_allegation.investigator.officer = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan'
        )
        result = InvestigatorAllegationSerializer(investigator_allegation).data
        expect(result['full_name']).to.eq('Jerome Finnigan')
        expect(result['abbr_name']).to.eq('J. Finnigan')
