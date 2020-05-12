from operator import attrgetter

from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory, AllegationFactory
from search.queries import BaseModelQuery, OfficerQuery, CrQuery, TrrQuery
from trr.factories import TRRFactory


class BaseModelQueryTestCase(TestCase):
    def test_queryset_raise_NotImplementedError(self):
        expect(lambda: BaseModelQuery(ids=[]).queryset()).to.throw(NotImplementedError)


class OfficerQueryTestCase(TestCase):
    def test_query(self):
        officer_1 = OfficerFactory(id=8562)
        officer_2 = OfficerFactory(id=8563)
        OfficerFactory(id=8564)
        results = sorted(list(OfficerQuery(ids=[8562, 8563]).query()), key=attrgetter('id'))
        expect(results).to.eq([officer_1, officer_2])


class CrQueryTestCase(TestCase):
    def test_query(self):
        allegation_1 = AllegationFactory(crid='C123')
        allegation_2 = AllegationFactory(crid='C456')
        AllegationFactory(crid='789')
        results = sorted(list(CrQuery(ids=['C123', 'C456']).query()), key=attrgetter('crid'))
        expect(results).to.eq([allegation_1, allegation_2])


class TrrQueryTestCase(TestCase):
    def test_query(self):
        trr_1 = TRRFactory(id=123)
        trr_2 = TRRFactory(id=456)
        TRRFactory(id=789)
        results = sorted(list(TrrQuery(ids=[123, 456]).query()), key=attrgetter('id'))
        expect(results).to.eq([trr_1, trr_2])
