from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from cr.serializers import InvolvementOfficerSerializer, CRSerializer
from data.factories import (
    OfficerFactory, AllegationFactory, AreaFactory, InvolvementFactory, OfficerBadgeNumberFactory
)


class InvolvementOfficerSerializerTestCase(TestCase):
    def test_get_extra_info(self):
        officer = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer, current=True, star=11111)
        result = InvolvementOfficerSerializer(officer).data
        expect(result['extra_info']).to.eq('Badge 11111')


class CRSerializerTestCase(TestCase):
    def test_get_point(self):
        allegation = AllegationFactory(point=None)
        result = CRSerializer(allegation).data
        expect(result['point']).to.eq(None)

        allegation = AllegationFactory(point=Point(1.0, 1.0))
        result = CRSerializer(allegation).data
        expect(result['point']).to.eq({'lon': 1.0, 'lat': 1.0})

    def test_get_involvements(self):
        allegation = AllegationFactory()
        investigator = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        OfficerBadgeNumberFactory(officer=investigator, current=True, star=11111)
        InvolvementFactory(
            allegation=allegation,
            involved_type='investigator',
            officer=investigator
        )

        commander = OfficerFactory(id=2, first_name='Eddie', last_name='Johnson')
        OfficerBadgeNumberFactory(officer=commander, current=True, star=11111)
        InvolvementFactory(
            allegation=allegation,
            involved_type='commander',
            officer=commander
        )

        result = CRSerializer(allegation).data
        self.assertListEqual(result['involvements'], [{
            'involved_type': 'investigator',
            'officers': [{
                'id': 1,
                'abbr_name': 'J. Finnigan',
                'extra_info': 'Badge 11111'
            }]
        }, {
            'involved_type': 'commander',
            'officers': [{
                'id': 2,
                'abbr_name': 'E. Johnson',
                'extra_info': 'Badge 11111'
            }]
        }])

    def test_get_beat(self):
        allegation = AllegationFactory(beat=None)
        result = CRSerializer(allegation).data
        expect(result['beat']).to.eq(None)

        allegation = AllegationFactory(beat=AreaFactory(name='23'))
        result = CRSerializer(allegation).data
        expect(result['beat']).to.eq('23')
