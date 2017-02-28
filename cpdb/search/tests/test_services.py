from django.test import TestCase

from robber import expect

from search.doc_types import OfficerDocType, FAQDocType
from search.services import SearchManager
from search.tests.utils import IndexMixin
from search.workers import OfficerWorker, FAQWorker


class SearchManagerTestCase(IndexMixin, TestCase):
    def test_search_with_content_type(self):
        response = SearchManager().search('fu na', content_type='UNIT')

        expect(response).to.eq({
            'UNIT': [],
        })

    def test_search(self):
        doc = OfficerDocType(full_name='full name', badge='123', url='url')
        doc.save()
        self.refresh_index()

        response = SearchManager().search('fu na')

        expect(response).to.eq({
            'UNIT': [],
            'NEIGHBORHOOD': [],
            'OFFICER': [{
                'url': 'url',
                'badge':
                '123',
                'full_name': u'full name'
            }],
            'COMMUNITY': []})

    def test_suggest_random(self):
        officerDoc = OfficerDocType(full_name='full name', badge='123', url='url')
        officerDoc.save()

        faqDoc = FAQDocType(question='I dont care', answer='-eh-eh-eh-eh-eh')
        faqDoc.save()

        self.refresh_index()

        response = SearchManager(
            workers={
                'OFFICER': OfficerWorker(),
                'FAQ': FAQWorker()
            }
        ).suggest_random()

        expect(response).to.eq({
            'FAQ': [{
                'question': 'I dont care',
                'answer': '-eh-eh-eh-eh-eh'
            }],
            'OFFICER': [{
                'url': 'url',
                'badge':
                '123',
                'full_name': u'full name'
            }]
        })
