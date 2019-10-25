from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch, Mock, mock_open
from robber import expect

from search.management.commands import rebuild_search_index


class RebuildSearchIndexCommandTestCase(SimpleTestCase):

    def setUp(self):
        self.indexer1 = Mock()
        self.doc_type1 = Mock()
        self.doc_type1._doc_type.name = 'a'
        self.indexer1.doc_type_klass = self.doc_type1
        self.indexer2 = Mock()
        self.doc_type2 = Mock()
        self.doc_type2._doc_type.name = 'b'
        self.indexer2.doc_type_klass = self.doc_type2

    def test_handle(self):
        with patch.object(rebuild_search_index, 'DEFAULT_INDEXERS', [self.indexer1, self.indexer2]):
            with patch('search.management.commands.rebuild_search_index.IndexerManager') as manager_mock:
                call_command('rebuild_search_index')
                expect(manager_mock.return_value.rebuild_index).to.be.called()

    def test_handle_one_doctype(self):
        with patch.object(rebuild_search_index, 'DEFAULT_INDEXERS', [self.indexer1, self.indexer2]):
            with patch('search.management.commands.rebuild_search_index.IndexerManager') as manager_mock:
                call_command('rebuild_search_index', 'a')
                expect(manager_mock).to.be.called_with([self.indexer1], [self.doc_type2])
                expect(manager_mock.return_value.rebuild_index).to.be.called()

    @patch('builtins.open', mock_open(read_data='["b"]'))
    def test_handle_read_file(self):
        with patch.object(rebuild_search_index, 'DEFAULT_INDEXERS', [self.indexer1, self.indexer2]):
            with patch('search.management.commands.rebuild_search_index.IndexerManager') as manager_mock:
                call_command('rebuild_search_index', '--from-file=test.json')
                expect(manager_mock).to.be.called_with([self.indexer2], [self.doc_type1])
                expect(manager_mock.return_value.rebuild_index).to.be.called()

    def test_handle_called_with_daily_option(self):
        with patch.object(rebuild_search_index, 'DEFAULT_INDEXERS', [self.indexer1, self.indexer2]):
            with patch.object(rebuild_search_index, 'DAILY_INDEXERS', [self.indexer2]):
                with patch('search.management.commands.rebuild_search_index.IndexerManager') as manager_mock:
                    call_command('rebuild_search_index', '--daily')
                    expect(manager_mock).to.be.called_with([self.indexer2], [self.doc_type1])
                    expect(manager_mock.return_value.rebuild_index).to.be.called()
