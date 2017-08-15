from mock import Mock, patch

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
        doc = OfficerDocType(meta={'id': '1'}, full_name='full name', badge='123', url='url')
        doc.save()
        self.refresh_index()

        response = SearchManager().search('fu na')

        expect(response).to.eq({
            'UNIT': [],
            'NEIGHBORHOOD': [],
            'OFFICER': [{
                'id': '1',
                'url': 'url',
                'badge': '123',
                'full_name': u'full name'
            }],
            'COMMUNITY': []})

    def test_suggest_sample(self):
        taglessOfficerDoc = OfficerDocType(
            meta={'id': '1'},
            full_name='this should not be returned',
            badge='123',
            url='url'
        )
        taglessOfficerDoc.save()

        officerDoc = OfficerDocType(
            meta={'id': '2'},
            full_name='full name',
            badge='123',
            url='url',
            tags=['sample']
        )
        officerDoc.save()

        faqDoc = FAQDocType(
            meta={'id': '11'},
            question='I dont care',
            answer='-eh-eh-eh-eh-eh',
            tags=['sample']
        )
        faqDoc.save()

        taglessFaqDoc = FAQDocType(
            meta={'id': '22'},
            question='this should not be returned',
            answer='nope'
        )
        taglessFaqDoc.save()

        self.refresh_index()

        response = SearchManager(
            workers={
                'OFFICER': OfficerWorker(),
                'FAQ': FAQWorker()
            }
        ).suggest_sample()

        expect(response).to.eq({
            'FAQ': [{
                'id': '11',
                'question': 'I dont care',
                'answer': '-eh-eh-eh-eh-eh',
                'tags': ['sample']
            }],
            'OFFICER': [{
                'id': '2',
                'url': 'url',
                'badge':
                '123',
                'full_name': u'full name',
                'tags': ['sample']
            }]
        })

    @patch('search.services.SimpleFormatter.format', return_value='formatter_results')
    def test_hooks(self, _):
        mock_hook = Mock()
        mock_worker = Mock()
        term = 'whatever'
        SearchManager(hooks=[mock_hook], workers={'mock': mock_worker}).search(term)
        mock_hook.execute.assert_called_with(term, None, {'mock': 'formatter_results'})
