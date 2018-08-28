from django.test import TestCase
from django.core.management import call_command

from mock import Mock, patch, mock_open

from es_index import indexer_klasses, indexer_klasses_map
from es_index.management.commands.rebuild_index import Command


class RebuildIndexCommandTestCase(TestCase):
    def _prepare_data(self, clear=True):
        class Indexer:
            index_alias = Mock(new_index_name='new_name')
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer.doc_type_klass._doc_type.name = 'a'
        Indexer.create_mapping = Mock()
        Indexer.add_new_data = Mock()
        Indexer.index_alias.name = 'test'
        Indexer.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer.index_alias.indexing.return_value.__enter__ = Mock()
        Indexer.index_alias.migrate = Mock()
        if clear:
            indexer_klasses_map['test'] = []
            del indexer_klasses[:]
        indexer_klasses_map['test'].append(Indexer)
        indexer_klasses.append(Indexer)
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

        indexer_klasses_map['alias'] = []
        indexer_klasses_map['alias'].append(Indexer1)
        indexer_klasses_map['alias'].append(Indexer2)
        del indexer_klasses[:]
        indexer_klasses.append(Indexer1)
        indexer_klasses.append(Indexer2)

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
        Indexer2.index_alias.migrate = Mock()
        Indexer2.create_mapping = Mock()
        Indexer2.add_new_data = Mock()
        indexer_klasses_map['test'].append(Indexer2)
        indexer_klasses.append(Indexer2)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index', 'test.a')

        Indexer1.create_mapping.assert_called_once()
        Indexer1.add_new_data.assert_called_once()
        Indexer1.index_alias.indexing.return_value.__exit__.assert_called_once()
        Indexer1.index_alias.indexing.return_value.__enter__.assert_called_once()

        Indexer2.add_new_data.assert_not_called()
        Indexer2.create_mapping.assert_called()
        Indexer2.index_alias.migrate.assert_not_called()

    def test_call_alias_indexing_with_multiple_doc_type_and_another_alias(self):
        Indexer1 = self._prepare_data()

        class Indexer2:
            index_alias = Mock(new_index_name='new_name')
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer2.doc_type_klass._doc_type.name = 'b'
        Indexer2.index_alias.name = 'test'
        Indexer2.index_alias.migrate = Mock()
        Indexer2.create_mapping = Mock()
        Indexer2.add_new_data = Mock()
        Indexer2.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer2.index_alias.indexing.return_value.__enter__ = Mock()
        indexer_klasses_map['test'].append(Indexer2)
        indexer_klasses.append(Indexer2)

        class Indexer3:
            index_alias = Mock()
            doc_type_klass = Mock(_doc_type=Mock())

        Indexer3.doc_type_klass._doc_type.name = 'c'
        Indexer3.index_alias.name = 'test2'
        Indexer3.index_alias.migrate = Mock()
        Indexer3.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer3.index_alias.indexing.return_value.__enter__ = Mock()
        Indexer3.create_mapping = Mock()
        Indexer3.add_new_data = Mock()
        indexer_klasses_map['test2'] = [Indexer3]
        indexer_klasses.append(Indexer3)

        with patch('es_index.management.commands.rebuild_index.autodiscover_modules'):
            call_command('rebuild_index', 'test.a', 'test.b', 'test2')

        Indexer1.create_mapping.assert_called_once()
        Indexer1.add_new_data.assert_called_once()

        Indexer2.add_new_data.assert_called()
        Indexer2.index_alias.migrate.assert_called()

        Indexer3.create_mapping.assert_called_once()
        Indexer3.add_new_data.assert_called_once()

    def test_rebuild_index_from_file(self):
        Indexer1 = self._prepare_data()
        with patch('__builtin__.open', mock_open(read_data='{"test": ["*"]}')) as mock_file:
            call_command('rebuild_index', '--from-file=indexers.json')
            mock_file.assert_called_with('indexers.json')
        Indexer1.create_mapping.assert_called_once()
        Indexer1.index_alias.migrate.assert_called_once()
        Indexer1.add_new_data.assert_called_once()

    def test_parent_indexers_should_be_index_first(self):
        rebuild_index_command = Command()
        Indexer1 = self._prepare_data()

        class Indexer2:
            index_alias = Indexer1.index_alias
            doc_type_klass = Indexer1.doc_type_klass
            parent_doc_type_property = 'children'

        Indexer2.doc_type_klass._doc_type.name = 'a'
        Indexer2.index_alias.name = 'test'
        Indexer2.index_alias.migrate = Mock()
        Indexer2.create_mapping = Mock()
        Indexer2.add_new_data = Mock()
        Indexer2.index_alias.indexing.return_value.__exit__ = Mock()
        Indexer2.index_alias.indexing.return_value.__enter__ = Mock()
        indexer_klasses_map['test'].append(Indexer2)
        indexer_klasses.append(Indexer2)

        self._prepare_data(clear=False)

        indexers = rebuild_index_command.get_indexers(app=['test.a'])
        self.assertEqual(len(indexers), 3)
        self.assertLess(indexers.index(Indexer1), indexers.index(Indexer2))
        self.assertEqual(indexers[-1], Indexer2)
