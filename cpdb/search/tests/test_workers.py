from django.test import SimpleTestCase

from robber import expect

from search.workers import FAQWorker, ReportWorker, OfficerWorker, UnitWorker, NeighborhoodsWorker, CommunityWorker
from search.doc_types import (FAQDocType, ReportDocType, OfficerDocType, UnitDocType, NeighborhoodsDocType,
                              CommunityDocType)
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
    def test_search(self):
        doc = OfficerDocType(
            full_name='full name', badge='123')
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('fu na')
        expect(response.hits.total).to.be.equal(1)


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
