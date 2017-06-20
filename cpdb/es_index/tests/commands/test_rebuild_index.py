from django.test import SimpleTestCase
from django.core.management import call_command

from mock import Mock, patch

from es_index import indexer_klasses, indexer_klasses_map


class RebuildIndexCommandTestCase(SimpleTestCase):
    def test_handle(self):
        class Indexer:
            index_alias = Mock()
        Indexer.reindex = Mock()
        Indexer.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer.index_alias.indexing.return_value.__enter__ = Mock()

        indexer_klasses.clear()
        indexer_klasses.add(Indexer)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index')

        Indexer.reindex.assert_called_once()
        Indexer.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer.index_alias.indexing.return_value.__enter__.assert_called_once()

    def test_call_with_app_specified(self):
        class Indexer:
            index_alias = Mock()
        Indexer.reindex = Mock()
        Indexer.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer.index_alias.indexing.return_value.__enter__ = Mock()

        indexer_klasses_map.setdefault('test', set()).clear()
        indexer_klasses_map['test'].add(Indexer)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index', 'test')

        Indexer.reindex.assert_called_once()
        Indexer.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer.index_alias.indexing.return_value.__enter__.assert_called_once()

    def test_call_alias_indexing_only_once_for_multiple_indexers(self):
        alias = Mock()
        alias.indexing.return_value.__exit__ = Mock()
        alias.indexing.return_value.__enter__ = Mock()

        class Indexer1:
            index_alias = alias
        Indexer1.reindex = Mock()

        class Indexer2:
            index_alias = alias
        Indexer2.reindex = Mock()

        indexer_klasses.clear()
        indexer_klasses.add(Indexer1)
        indexer_klasses.add(Indexer2)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index')

        Indexer1.reindex.assert_called_once()
        Indexer2.reindex.assert_called_once()
        alias.indexing.return_value.__exit__.assert_called_once()
        alias.indexing.return_value.__enter__.assert_called_once()
