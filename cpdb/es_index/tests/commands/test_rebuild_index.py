from django.test import SimpleTestCase
from django.core.management import call_command

from mock import Mock, patch

from es_index import indexer_klasses, indexer_klasses_map


class RebuildIndexCommandTestCase(SimpleTestCase):
    def _prepare_data(self):
        class Indexer:
            index_alias = Mock(new_index_name='new_name')
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer.doc_type_klass._doc_type.name = 'a'
        Indexer.create_mapping = Mock()
        Indexer.add_new_data = Mock()
        Indexer.index_alias.name = 'test'
        Indexer.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer.index_alias.indexing.return_value.__enter__ = Mock()
        indexer_klasses_map.setdefault('test', set()).clear()
        indexer_klasses_map['test'].add(Indexer)
        indexer_klasses.clear()
        indexer_klasses.add(Indexer)
        return Indexer

    def test_handle(self):
        Indexer = self._prepare_data()

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index')

        Indexer.create_mapping.assert_called_once()
        Indexer.add_new_data.assert_called_once()
        Indexer.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer.index_alias.indexing.return_value.__enter__.assert_called_once()

    def test_call_with_app_specified(self):
        Indexer = self._prepare_data()

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index', 'test')

        Indexer.create_mapping.assert_called_once()
        Indexer.add_new_data.assert_called_once()
        Indexer.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer.index_alias.indexing.return_value.__enter__.assert_called_once()

    def test_call_alias_indexing_only_once_for_multiple_indexers(self):
        alias = Mock()
        alias.name = 'alias'
        alias.indexing.return_value.__exit__ = Mock()
        alias.indexing.return_value.__enter__ = Mock()

        class Indexer1:
            index_alias = alias
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer1.create_mapping = Mock()
        Indexer1.add_new_data = Mock()

        class Indexer2:
            index_alias = alias
            doc_type_klass = Mock(_doc_type=Mock(name='b'))

        Indexer2.create_mapping = Mock()
        Indexer2.add_new_data = Mock()

        indexer_klasses_map.setdefault('alias', set()).clear()
        indexer_klasses_map['alias'].add(Indexer1)
        indexer_klasses_map['alias'].add(Indexer2)
        indexer_klasses.clear()
        indexer_klasses.add(Indexer1)
        indexer_klasses.add(Indexer2)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index')

        Indexer1.create_mapping.assert_called_once()
        Indexer2.create_mapping.assert_called_once()
        Indexer1.add_new_data.assert_called_once()
        Indexer2.add_new_data.assert_called_once()
        alias.indexing.return_value.__exit__.assert_called_once()
        alias.indexing.return_value.__enter__.assert_called_once()

    def test_call_alias_indexing_with_specific_doc_type(self):
        Indexer1 = self._prepare_data()

        class Indexer2:
            index_alias = Mock(new_index_name='new_name')
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer2.doc_type_klass._doc_type.name = 'b'
        Indexer2.index_alias.name = 'test'
        Indexer2.create_mapping = Mock()
        Indexer2.add_new_data = Mock()
        indexer_klasses_map['test'].add(Indexer2)
        indexer_klasses.add(Indexer2)

        with patch('es_index.es_client.reindex') as mock_reindex:
            with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
                call_command('rebuild_index', 'test.a')

            mock_reindex.assert_called_once()

        Indexer1.create_mapping.assert_called_once()
        Indexer1.add_new_data.assert_called_once()
        Indexer2.add_new_data.assert_not_called()
        Indexer1.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer1.index_alias.indexing.return_value.__enter__.assert_called_once()
