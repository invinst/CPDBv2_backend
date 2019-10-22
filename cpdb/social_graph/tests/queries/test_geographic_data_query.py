from django.test import TestCase

from robber import expect

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory
from social_graph.queries.geographic_data_query import GeographyCrsDataQuery, GeographyTrrsDataQuery
from trr.factories import TRRFactory


class GeographyCrsDataQueryTestCase(TestCase):
    def test_data(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officers = [officer_1, officer_2, officer_3, officer_4]

        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')
        AllegationFactory(crid='987')
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_1
        )
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_2
        )
        OfficerAllegationFactory(
            officer=officer_2,
            allegation=allegation_2
        )

        expected_data = [allegation_1.crid, allegation_2.crid, allegation_3.crid]
        results = [item.crid for item in list(GeographyCrsDataQuery([allegation_3.crid], officers).data())]
        expect(results).to.eq(expected_data)


class GeographyTrrsDataQueryTestCase(TestCase):
    def test_data(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officer_5 = OfficerFactory(id=5)
        officers = [officer_1, officer_2, officer_3, officer_4]

        trr_1 = TRRFactory(id=1, officer=officer_3)
        trr_2 = TRRFactory(id=2, officer=officer_4)
        trr_3 = TRRFactory(id=3, officer=officer_4)
        TRRFactory(id=4, officer=officer_5)

        expected_data = [trr_1.id, trr_2.id, trr_3.id]
        results = [item.id for item in list(GeographyTrrsDataQuery([trr_3.id], officers).data())]
        expect(results).to.eq(expected_data)
