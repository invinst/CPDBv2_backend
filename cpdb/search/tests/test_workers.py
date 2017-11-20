from django.test import SimpleTestCase

from robber import expect

from search.workers import (
    FAQWorker, ReportWorker, OfficerWorker, UnitWorker, UnitOfficerWorker,
    NeighborhoodsWorker, CommunityWorker, CoAccusedOfficerWorker)
from search.doc_types import (
    FAQDocType, ReportDocType, OfficerDocType, UnitDocType, UnitOfficerDocType,
    NeighborhoodsDocType, CommunityDocType, CoAccusedOfficerDocType)
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
        doc = OfficerDocType(
            full_name='full name', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerDocType(
            full_name='funny naga', badge='456', allegation_count=20)
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('fu na')

        expect(response.hits.total).to.be.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('funny naga')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('full name')

    def test_search_prioritizing_tags(self):
        doc = OfficerDocType(
            full_name='some dude', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerDocType(
            full_name='another guy', badge='456', allegation_count=10, tags='somersault')
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('some')

        expect(response.hits.total).to.be.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('another guy')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('some dude')

    def test_search_by_officer_id(self):
        doc = OfficerDocType(full_name='some dude', badge='123', meta={'_id': '456'})
        doc.save()
        doc2 = OfficerDocType(full_name='another guy', badge='789', meta={'_id': '012'})
        doc2.save()

        self.refresh_index()

        response = OfficerWorker().search('456')

        expect(response.hits.total).to.be.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('some dude')


class UnitWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = UnitDocType(name='name')
        doc.save()

        self.refresh_index()

        response = UnitWorker().search('name')
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


class CoAccusedOfficerWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = CoAccusedOfficerDocType(
            full_name='Kevin Osborn', co_accused_officer=[{
                'full_name': 'Cristiano Ronaldo',
                'badge': '123'
            }])
        doc.save()

        self.refresh_index()

        response = CoAccusedOfficerWorker().search('Cris')
        expect(response.hits.total).to.be.equal(1)
        co_accused_doc = response.hits[0]
        expect(co_accused_doc.full_name).to.eq('Kevin Osborn')
        expect(co_accused_doc.co_accused_officer[0]['full_name']).to.eq('Cristiano Ronaldo')


class UnitOfficerWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
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
