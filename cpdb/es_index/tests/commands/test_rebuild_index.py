from django.test import SimpleTestCase
from django.core.management import call_command

from mock import Mock, patch

from es_index import indexer_klasses, index_klasses, index_klasses_map, indexer_klasses_map


class RebuildIndexCommandTestCase(SimpleTestCase):
    def test_handle(self):
        index_klass = Mock()
        index_klass.delete = Mock()
        index_klass.create = Mock()

        class Indexer:
            pass
        Indexer.reindex = Mock()

        indexer_klasses.clear()
        indexer_klasses.add(Indexer)

        index_klasses.clear()
        index_klasses.add(index_klass)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index')

        index_klass.create.assert_called_once()
        index_klass.delete.assert_called_once_with(ignore=404)
        Indexer.reindex.assert_called_once()

    def test_call_with_app_specified(self):
        index_klass = Mock()
        index_klass.delete = Mock()
        index_klass.create = Mock()

        class Indexer:
            pass
        Indexer.reindex = Mock()

        index_klasses_map.setdefault('test', set()).clear()
        index_klasses_map['test'].add(index_klass)

        indexer_klasses_map.setdefault('test', set()).clear()
        indexer_klasses_map['test'].add(Indexer)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index', 'test')

        index_klass.create.assert_called_once()
        index_klass.delete.assert_called_once_with(ignore=404)
        Indexer.reindex.assert_called_once()
