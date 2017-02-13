from django.test import SimpleTestCase
from django.core.management import call_command

from mock import Mock, patch

from es_index import indexer_klasses, index_klasses


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
