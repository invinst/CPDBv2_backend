from django.test import TestCase

from robber import expect

from data.factories import AreaFactory, OfficerFactory, PoliceUnitFactory
from search_terms.term_builders import (
    AreaTermBuilder, PoliceDistrictsTermBuilder, CommunitiesTermBuilder, NeighborhoodsTermBuilder,
    PoliceBeatTermBuilder, SchoolGroundsTermBuilder, WardsTermBuilder, get_term_builders,
    OfficerRankTermBuilder, PoliceUnitTermBuilder
)


class AreaTermBuilderTestCase(TestCase):
    def test_build_terms(self):
        class MyAreaTermBuilder(AreaTermBuilder):
            slug = 'my_area_type'
            query_key = 'my_query_key'

        AreaFactory(area_type='my_area_type', name='1st')
        AreaFactory(area_type='my_area_type', name='2nd')
        expect(MyAreaTermBuilder.build_terms()).to.eq([
            {
                'name': '1st',
                'link': 'https://data.cpdp.co/url-mediator/session-builder?my_query_key=1st'
            }, {
                'name': '2nd',
                'link': 'https://data.cpdp.co/url-mediator/session-builder?my_query_key=2nd'
            }
        ])


class GetTermBuildersTestCase(TestCase):
    def test_call(self):
        expect(get_term_builders('police-districts')).to.eq(PoliceDistrictsTermBuilder)
        expect(get_term_builders('community')).to.eq(CommunitiesTermBuilder)
        expect(get_term_builders('neighborhoods')).to.eq(NeighborhoodsTermBuilder)
        expect(get_term_builders('police-beats')).to.eq(PoliceBeatTermBuilder)
        expect(get_term_builders('school-grounds')).to.eq(SchoolGroundsTermBuilder)
        expect(get_term_builders('wards')).to.eq(WardsTermBuilder)


class OfficerRankTermBuilderTestCase(TestCase):
    def test_build_terms(self):
        OfficerFactory(rank='my-custom-rank')
        expect(OfficerRankTermBuilder.build_terms()).to.eq([{
            'name': 'my-custom-rank',
            'link': 'https://data.cpdp.co/url-mediator/session-builder?officer__rank=my-custom-rank'
        }])


class PoliceUnitTermBuilderTestCase(TestCase):
    def test_build_terms(self):
        PoliceUnitFactory(unit_name='001', description='my unit description')
        expect(PoliceUnitTermBuilder.build_terms()).to.eq([{
            'name': 'my unit description',
            'link': 'https://data.cpdp.co/url-mediator/session-builder?officer__unit=001'
        }])
