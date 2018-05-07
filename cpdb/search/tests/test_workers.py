from django.test import SimpleTestCase

from robber import expect

from search.workers import (
    FAQWorker, ReportWorker, OfficerWorker, UnitWorker, UnitOfficerWorker,
    NeighborhoodsWorker, CommunityWorker, CrWorker
)
from search.doc_types import (
    FAQDocType, ReportDocType, UnitDocType, UnitOfficerDocType,
    NeighborhoodsDocType, CommunityDocType, CrDocType
)
from officers.doc_types import OfficerInfoDocType
from search.tests.utils import IndexMixin


class FAQWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = FAQDocType(question='question', answer='answer')
        doc.save()

        self.refresh_index()

        response = FAQWorker().search('question')
        expect(response.hits.total).to.be.equal(1)


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
        doc = NeighborhoodsDocType(name='name')
        doc.save()

        self.refresh_index()

        response = NeighborhoodsWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class CommunityWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = CommunityDocType(name='name')
        doc.save()

        self.refresh_index()

        response = CommunityWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class UnitOfficerWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_by_unit_name(self):
        doc = UnitOfficerDocType(unit_name='001', full_name='Kevin Osborn', allegation_count=1)
        doc.save()
        doc = UnitOfficerDocType(unit_name='001', full_name='Kevin Cascone', allegation_count=0)
        doc.save()
        doc = UnitOfficerDocType(unit_name='002', full_name='Cristiano Cascone', allegation_count=0)
        doc.save()

        self.refresh_index()

        response = UnitOfficerWorker().search('001')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')

    def test_search_by_unit_description(self):
        doc = UnitOfficerDocType(unit_description='foo', full_name='Kevin Osborn', allegation_count=1)
        doc.save()
        doc = UnitOfficerDocType(unit_description='foo', full_name='Kevin Cascone', allegation_count=0)
        doc.save()
        doc = UnitOfficerDocType(unit_description='bar', full_name='Cristiano Cascone', allegation_count=0)
        doc.save()

        self.refresh_index()

        response = UnitOfficerWorker().search('foo')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')


class CrWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = CrDocType(crid='123456')
        doc.save()

        self.refresh_index()

        response = CrWorker().search('123456')
        expect(response.hits.total).to.be.equal(1)
