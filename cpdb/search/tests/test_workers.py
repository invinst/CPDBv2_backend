from django.test import SimpleTestCase, TestCase

from robber import expect

from data.factories import OfficerFactory, OfficerAllegationFactory, OfficerHistoryFactory, PoliceUnitFactory
from search.workers import (
    ReportWorker, OfficerWorker, UnitWorker, UnitOfficerWorker,
    NeighborhoodsWorker, CommunityWorker, CrWorker, AreaWorker, TRRWorker
)
from search.doc_types import ReportDocType, UnitDocType, AreaDocType, CrDocType, TRRDocType
from officers.doc_types import OfficerInfoDocType
from search.tests.utils import IndexMixin


class ReportWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = ReportDocType(
            publication='publication', title='title',
            author='author', excerpt='excerpt')
        doc.save()

        self.refresh_index()

        response = ReportWorker().search('author')
        expect(response.hits.total).to.be.equal(1)


class OfficerWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_prioritizing_allegation_count(self):
        doc = OfficerInfoDocType(
            full_name='full name', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerInfoDocType(
            full_name='funny naga', badge='456', allegation_count=20)
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('fu na')

        expect(response.hits.total).to.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('funny naga')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('full name')

    def test_search_prioritizing_tags(self):
        doc = OfficerInfoDocType(
            full_name='some dude', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerInfoDocType(
            full_name='another guy', badge='456', allegation_count=10, tags='somersault')
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('some')

        expect(response.hits.total).to.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('another guy')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('some dude')

    def test_search_by_officer_id(self):
        doc = OfficerInfoDocType(full_name='some dude', badge='123', meta={'_id': '456'})
        doc.save()
        doc2 = OfficerInfoDocType(full_name='another guy', badge='789', meta={'_id': '012'})
        doc2.save()

        self.refresh_index()

        response = OfficerWorker().search('456')

        expect(response.hits.total).to.be.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('some dude')

    def test_search_officer_badge(self):
        OfficerInfoDocType(full_name='John Doe', badge='100123').save()

        self.refresh_index()

        response = OfficerWorker().search('100')

        expect(response.hits.total).to.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('John Doe')

    def test_search_officer_historic_badge(self):
        OfficerInfoDocType(full_name='John Doe', historic_badges=['100123', '123456']).save()

        self.refresh_index()

        response = OfficerWorker().search('100')

        expect(response.hits.total).to.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('John Doe')

    # Note: We've found that scoring of elasticsearch is incredibly complex and could not
    # be easily replicated in unit tests. Therefore we decided to stop adding tests to this
    # particular test case and instead rely more on manual testing.


class UnitWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_by_name(self):
        doc = UnitDocType(name='name')
        doc.save()

        self.refresh_index()

        response = UnitWorker().search('name')
        expect(response.hits.total).to.be.equal(1)

    def test_search_by_description(self):
        doc = UnitDocType(description='foo bar')
        doc.save()

        self.refresh_index()

        response = UnitWorker().search('foo')
        expect(response.hits.total).to.be.equal(1)


class NeighborhoodsWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = AreaDocType(name='name', area_type='neighborhood')
        doc.save()

        self.refresh_index()

        response = NeighborhoodsWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class CommunityWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = AreaDocType(name='name', area_type='community')
        doc.save()

        self.refresh_index()

        response = CommunityWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class AreaWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_sort_by_name(self):
        doc = AreaDocType(name='name1', area_type='community')
        doc.save()
        doc = AreaDocType(name='name2')
        doc.save()

        self.refresh_index()

        response = AreaWorker().search('name')
        expect(response.hits.total).to.be.equal(2)
        expect(response[0].name).to.be.eq('name1')
        expect(response[1].name).to.be.eq('name2')

    def test_search_sort_by_allegation_count(self):
        doc1 = AreaDocType(name='name1', area_type='community', allegation_count=101)
        doc2 = AreaDocType(name='name2', area_type='community', allegation_count=201)
        doc3 = AreaDocType(name='name3', area_type='community', allegation_count=201)

        doc1.save()
        doc2.save()
        doc3.save()

        self.refresh_index()

        response = AreaWorker().search('name')
        expect(response.hits.total).to.be.equal(3)
        expect(response[0].name).to.be.eq('name2')
        expect(response[1].name).to.be.eq('name3')
        expect(response[2].name).to.be.eq('name1')


class UnitOfficerWorkerTestCase(IndexMixin, TestCase):
    def setUp(self):
        super(UnitOfficerWorkerTestCase, self).setUp()
        officer1 = OfficerFactory(first_name='Kevin', last_name='Osborn')
        officer2 = OfficerFactory(first_name='Kevin', last_name='Cascone')
        officer3 = OfficerFactory(first_name='Cristiano', last_name='Cascone')
        OfficerAllegationFactory(officer=officer1)
        unit1 = PoliceUnitFactory(unit_name='001', description='foo')
        OfficerHistoryFactory(officer=officer1, unit=unit1)
        OfficerHistoryFactory(officer=officer2, unit=unit1)
        OfficerHistoryFactory(officer=officer3, unit__unit_name='002', unit__description='bar')
        self.rebuild_index()
        self.refresh_index()

    def test_search_by_unit_name(self):
        response = UnitOfficerWorker().search('001')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')

    def test_search_by_unit_description(self):
        response = UnitOfficerWorker().search('foo')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')


class CrWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        CrDocType(crid='123456', incident_date='2007-12-27').save()
        CrDocType(crid='890', incident_date='2008-12-27').save()
        CrDocType(crid='678', incident_date='2009-12-27').save()
        self.refresh_index()

        response = CrWorker().search('123456', dates=['2008-12-27'])
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit.crid for hit in response.hits])).to.be.eq({'123456', '890'})


class TRRWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        TRRDocType(_id='123456', trr_datetime='2007-12-27').save()
        TRRDocType(_id='890', trr_datetime='2008-12-27').save()
        TRRDocType(_id='678', trr_datetime='2009-12-27').save()
        self.refresh_index()

        response = TRRWorker().search('123456', dates=['2008-12-27'])
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit._id for hit in response.hits])).to.be.eq({'123456', '890'})
