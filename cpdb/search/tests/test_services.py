from mock import Mock, patch

from django.test import TestCase

from robber import expect

from search.services import SearchManager
from search.tests.utils import IndexMixin
from search.workers import OfficerWorker
from officers.doc_types import OfficerInfoDocType


class SearchManagerTestCase(IndexMixin, TestCase):
    def test_search_with_content_type(self):
        response = SearchManager().search('fu na', content_type='UNIT')

        expect(response).to.eq({
            'UNIT': [],
        })

    def test_search(self):
        doc = OfficerInfoDocType(meta={'id': '1'}, full_name='full name', badge='123', url='url')
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
        taglessOfficerDoc = OfficerInfoDocType(
            meta={'id': '1'},
            full_name='this should not be returned',
            badge='123',
            url='url'
        )
        taglessOfficerDoc.save()

        officerDoc = OfficerInfoDocType(
            meta={'id': '2'},
            full_name='full name',
            badge='123',
            url='url',
            tags=['sample']
        )
        officerDoc.save()

        self.refresh_index()

        response = SearchManager(
            workers={
                'OFFICER': OfficerWorker(),
            }
        ).suggest_sample()

        expect(response).to.eq({
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

    @patch('search.services.OfficerWorker.query', return_value='abc')
    def test_get_search_query_for_type(self, patched_query):
        query = SearchManager().get_search_query_for_type('term', 'OFFICER')
        patched_query.assert_called_with('term')
        expect(query).to.eq('abc')

    def test_get_formatted_results(self):
        mock_document = Mock(to_dict=Mock(return_value={'a': 'b'}), _id=123)
        formatted_results = SearchManager().get_formatted_results([mock_document], 'SIMPLE')
        expect(formatted_results).to.eq([{
            'a': 'b',
            'id': 123
        }])
