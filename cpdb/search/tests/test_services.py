from django.test import TestCase

from mock import Mock, patch
from robber import expect

from search.services import SearchManager
from search.tests.utils import IndexMixin
from search.workers import DateCRWorker, OfficerWorker
from search.doc_types import CrDocType
from officers.doc_types import OfficerInfoDocType


class SearchManagerTestCase(IndexMixin, TestCase):
    def test_search_with_content_type(self):
        response = SearchManager().search('fu na', content_type='UNIT')

        expect(response).to.eq({
            'UNIT': [],
        })

    def test_search(self):
        OfficerInfoDocType(meta={'id': '1'}, full_name='full name', badge='123', url='url').save()
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

    def test_search_with_date(self):
        OfficerInfoDocType(meta={'id': '1'}, full_name='full name', badge='123', url='url').save()
        CrDocType(meta={'id': '1'}, crid='1234', incident_date='2017-12-27').save()
        self.refresh_index()

        workers = {
            'OFFICER': OfficerWorker(),
            'DATE > CR': DateCRWorker(),
        }
        response = SearchManager(workers=workers).search('fu na 2017-12-27')
        expect(response).to.eq({
            'OFFICER': [{
                'id': '1',
                'url': 'url',
                'badge': '123',
                'full_name': u'full name'
            }],
            'DATE > CR': [{
                'id': '1',
                'crid': '1234',
                'incident_date': '2017-12-27'
            }]
        })

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

    def test_search_without_spaces(self):
        OfficerInfoDocType(meta={'id': '1'}, full_name='Kevin Mc Donald', badge='123', url='url').save()
        OfficerInfoDocType(meta={'id': '2'}, full_name='John Mcdonald', badge='123', url='url').save()
        self.refresh_index()
        response = SearchManager().search('McDonald')
        response1 = SearchManager().search('Mc Donald')

        expect(response['OFFICER']).to.eq([{
            'id': '1',
            'url': 'url',
            'badge': '123',
            'full_name': u'Kevin Mc Donald'
        }, {
            'id': '2',
            'url': 'url',
            'badge': '123',
            'full_name': u'John Mcdonald'
        }])

        expect(response1['OFFICER']).to.eq([{
            'id': '1',
            'url': 'url',
            'badge': '123',
            'full_name': u'Kevin Mc Donald'
        }, {
            'id': '2',
            'url': 'url',
            'badge': '123',
            'full_name': u'John Mcdonald'
        }])

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
        patched_query.assert_called_with('term', dates=[])
        expect(query).to.eq('abc')

    @patch('search.workers.DateCRWorker.query', return_value='abc')
    def test_get_search_query_for_type_with_date(self, patched_query):
        workers = {
            'DATE > CR': DateCRWorker()
        }
        query = SearchManager(workers=workers).get_search_query_for_type('term 2017-12-27', 'DATE > CR')
        patched_query.assert_called_with('term 2017-12-27', dates=['2017-12-27'])
        expect(query).to.eq('abc')

    def test_get_formatted_results(self):
        mock_document = Mock(
            to_dict=Mock(return_value={'a': 'b'}),
            _id=123,
            meta=Mock(
                spec=[]
            )
        )
        formatted_results = SearchManager().get_formatted_results([mock_document], 'SIMPLE')
        expect(formatted_results).to.eq([{
            'a': 'b',
            'id': 123
        }])
