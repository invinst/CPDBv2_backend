from django.test import SimpleTestCase

from elasticsearch_dsl import DocType
from robber import expect
from mock import Mock, patch

from es_index.indexers import BaseIndexer, es_client


class IndexersTestCase(SimpleTestCase):

    def test_get_queryset(self):
        expect(lambda: BaseIndexer().get_queryset()).to.throw(NotImplementedError)

    def test_extract_datum(self):
        expect(lambda: BaseIndexer().extract_datum('anything')).to.throw(NotImplementedError)

    def test_docs_when_extract_datum_is_generator(self):
        class MyDocType(DocType):
            pass

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = Mock(new_index_name='new_index_name')

            def get_queryset(self):
                return [1]

            def extract_datum(self, datum):
                yield {'a': 'b'}

        indexer = ConcreteIndexer()
        expect(list(indexer.docs())).to.eq([{
            '_type': 'my_doc_type',
            '_source': {'a': 'b'},
            '_index': 'new_index_name'
        }])

    def test_docs_when_extract_datum_return_single_value(self):
        class MyDocType(DocType):
            pass

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = Mock(new_index_name='new_index_name')

            def get_queryset(self):
                return [1]

            def extract_datum(self, datum):
                return {'a': 'b'}

        indexer = ConcreteIndexer()
        expect(list(indexer.docs())).to.eq([{
            '_type': 'my_doc_type',
            '_source': {'a': 'b'},
            '_index': 'new_index_name'
        }])

    def test_add_meta_id_when_there_is_id_in_raw_doc(self):
        class MyDocType(DocType):
            pass

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = Mock(new_index_name='new_index_name')

            def get_queryset(self):
                return [1]

            def extract_datum(self, datum):
                return {'a': 'b', 'id': 1}

        indexer = ConcreteIndexer()
        expect(list(indexer.docs())).to.eq([{
            '_type': 'my_doc_type',
            '_source': {'a': 'b', 'id': 1},
            '_index': 'new_index_name',
            '_id': 1
        }])

    def test_add_meta_and_script_when_parent_doc_type_property_is_set(self):
        class MyDocType(DocType):
            pass

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = Mock(new_index_name='new_index_name')
            parent_doc_type_property = 'children'

            def get_queryset(self):
                return [1]

            def extract_datum(self, datum):
                return {'a': 'b', 'id': 1}

        indexer = ConcreteIndexer()
        expect(list(indexer.docs())).to.eq([{
            '_type': 'my_doc_type', '_id': 1,
            '_source': {
                'upsert': {'id': 1, 'children': [{'a': 'b', 'id': 1}]},
                'script': {
                    'lang': 'painless',
                    'inline': "if (!ctx._source.containsKey('children')) { ctx._source.children = [] } "
                              "ctx._source.children.add(params.new_doc)",
                    'params': {'new_doc': {'a': 'b', 'id': 1}}
                }},
            '_op_type': 'update', '_index': 'new_index_name'
        }])

    def test_init_doc_type_when_create_mapping(self):
        init_mock = Mock()

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = Mock(init=init_mock)
            index_alias = Mock(new_index_name='new_index_name')

        ConcreteIndexer().create_mapping()
        expect(init_mock).to.be.called()

    def test_dont_init_doc_type_when_parent_doc_type_property_is_set(self):
        init_mock = Mock()

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = Mock(init=init_mock)
            index_alias = Mock(new_index_name='new_index_name')
            parent_doc_type_property = 'children'

        ConcreteIndexer().create_mapping()
        expect(init_mock).not_to.be.called()

    @patch('es_index.indexers.bulk')
    def test_reindex(self, mock_bulk):
        mock_write_index = Mock()
        mock_init = Mock()
        indexer = BaseIndexer()
        indexer.docs = Mock(return_value=[1])
        indexer.index_alias = Mock(write_index=mock_write_index, new_index_name='new_index_name')
        indexer.doc_type_klass = Mock(init=mock_init)

        indexer.reindex()

        expect(mock_write_index.open.called).to.be.true()
        expect(mock_write_index.close.called).to.be.true()
        expect(mock_write_index.settings.called).to.be.true()
        expect(mock_init.called).to.be.true()
        expect(mock_bulk.calledWith(es_client, [1]))
