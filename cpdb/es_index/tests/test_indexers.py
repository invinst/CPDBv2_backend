from django.test import SimpleTestCase, TestCase

from elasticsearch_dsl import DocType, Keyword, Float, Mapping
from robber import expect
from mock import Mock, patch

from es_index.indexers import BaseIndexer, es_client, PartialIndexer
from es_index.index_aliases import IndexAlias
from es_index import register_indexer


class IndexersTestCase(SimpleTestCase):

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
            '_index': 'new_index_name',
            '_op_type': 'index'
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
            '_index': 'new_index_name',
            '_op_type': 'index'
        }])

    def test_docs_when_op_type_is_update(self):
        class MyDocType(DocType):
            pass

        class ConcreteIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = Mock(new_index_name='new_index_name')
            op_type = 'update'

            def get_queryset(self):
                return [1]

            def extract_datum(self, datum):
                return {'id': 1, 'a': 'b'}

        indexer = ConcreteIndexer()
        expect(list(indexer.docs())).to.eq([{
            '_id': 1,
            '_type': 'my_doc_type',
            '_source': {'doc': {'a': 'b'}},
            '_index': 'new_index_name',
            '_op_type': 'update'
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
            '_id': 1,
            '_op_type': 'index'
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


my_index_alias = IndexAlias('my_alias')


@my_index_alias.doc_type
class MyDocType(DocType):
    id = Keyword()
    value = Float()

    class Meta:
        doc_type = 'my_doc_type'


class PartialIndexerTestCase(TestCase):
    def setUp(self):
        my_index_alias.read_index.delete(ignore=404)
        my_index_alias.read_index.create(ignore=400)

    def test_get_batch_queryset(self):
        expect(lambda: PartialIndexer().get_batch_queryset([])).to.throw(NotImplementedError)

    def test_get_batch_update_docs_queries(self):
        expect(lambda: PartialIndexer().get_batch_update_docs_queries([])).to.throw(NotImplementedError)

    def test_batch_querysets(self):
        class MyPartialIndexer(PartialIndexer):
            batch_size = 2

            def get_batch_queryset(self, keys):
                return keys

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        expect(list(my_indexer.batch_querysets)).to.eq([[1, 2], [3]])

    def test_batch_update_docs_queries(self):
        class MyPartialIndexer(PartialIndexer):
            batch_size = 2

            def get_batch_update_docs_queries(self, keys):
                return keys

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        expect(list(my_indexer.batch_update_docs_queries)).to.eq([[1, 2], [3]])

    def test_get_queryset(self):
        class MyPartialIndexer(PartialIndexer):
            batch_size = 2

            def get_batch_queryset(self, keys):
                return keys

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        expect(list(my_indexer.get_queryset())).to.eq([1, 2, 3])

    def test_validate_updated_docs(self):
        class MyPartialIndexer(PartialIndexer):
            batch_size = 2

            def get_postgres_count(self, keys):
                return len(keys)

            def get_batch_update_docs_queries(self, keys):
                return Mock(count=Mock(return_value=len(keys)))

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        expect(my_indexer.validate_updated_docs()).to.be.none()

    def test_validate_updated_docs_raise_ValueError(self):
        class MyPartialIndexer(PartialIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias
            batch_size = 2

            def get_postgres_count(self, keys):
                return len(keys)

            def get_batch_update_docs_queries(self, keys):
                return Mock(count=Mock(return_value=1))

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        expect(lambda: my_indexer.validate_updated_docs()).to.throw(ValueError)

    def test_delete_existing_docs(self):
        class MyPartialIndexer(PartialIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias
            batch_size = 2

            def get_batch_update_docs_queries(self, keys):
                return self.doc_type_klass.search().query('terms', id=keys)

        MyDocType(id=1).save()
        MyDocType(id=2).save()
        my_index_alias.read_index.refresh()

        my_indexer = MyPartialIndexer(updating_keys=[1])

        expect(MyDocType.search().count()).to.equal(2)

        my_index_alias.write_index.create(ignore=400)
        my_indexer.index_alias.migrate()
        expect(my_index_alias.write_index.search().count()).to.equal(2)

        my_indexer.delete_existing_docs()

        expect(my_index_alias.write_index.search().count()).to.equal(1)
        expect(my_index_alias.write_index.search().query('term', id=2).count()).to.equal(1)

        my_index_alias.write_index.delete(ignore=404)

    def test_reindex_raise_ValueError_first(self):
        class MyPartialIndexer(PartialIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias
            batch_size = 2

            def get_postgres_count(self, keys):
                return len(keys)

            def get_batch_update_docs_queries(self, keys):
                return Mock(count=Mock(return_value=1))

        my_indexer = MyPartialIndexer(updating_keys=[1, 2, 3])
        my_indexer.create_mapping = Mock()
        my_indexer.migrate = Mock()
        my_indexer.delete_existing_docs = Mock()
        my_indexer.add_new_data = Mock()

        expect(lambda: my_indexer.reindex()).to.throw(ValueError)

        expect(my_indexer.create_mapping).not_to.be.called()
        expect(my_indexer.migrate).not_to.be.called()
        expect(my_indexer.delete_existing_docs).not_to.be.called()
        expect(my_indexer.add_new_data).not_to.be.called()

    def test_reindex_raise_ValueError(self):
        class MyPartialIndexer(PartialIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias
            batch_size = 2

            def get_postgres_count(self, keys):
                return 0

            def get_batch_update_docs_queries(self, keys):
                return self.doc_type_klass.search().query('terms', id=keys)

            def extract_datum(self, datum):
                return {'id': datum.id}

        MyDocType(id=1).save()
        MyDocType(id=2).save()
        MyDocType(id=3).save()
        my_index_alias.read_index.refresh()

        my_indexer = MyPartialIndexer(updating_keys=[1, 2])
        expect(lambda: my_indexer.reindex()).to.throw(ValueError)

    def test_reindex(self):
        class MyPartialIndexer(PartialIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias
            batch_size = 2

            def get_batch_queryset(self, keys):
                return Mock(
                    __iter__=Mock(return_value=iter([Mock(id=key, value=key + 10) for key in keys]))
                )

            def get_postgres_count(self, keys):
                return len(keys)

            def get_batch_update_docs_queries(self, keys):
                return self.doc_type_klass.search().query('terms', id=keys)

            def extract_datum(self, datum):
                return {'id': datum.id, 'value': datum.value}

        for value in [1, 2, 3]:
            MyDocType(id=value, value=value).save()
        my_index_alias.read_index.refresh()

        expect(MyDocType.search().count()).to.equal(3)
        expect(MyDocType.search().query('term', id=1).execute()[0].to_dict()['value']).to.equal(1)
        expect(MyDocType.search().query('term', id=2).execute()[0].to_dict()['value']).to.equal(2)
        expect(MyDocType.search().query('term', id=3).execute()[0].to_dict()['value']).to.equal(3)

        my_indexer = MyPartialIndexer(updating_keys=[1, 2])

        with my_indexer.index_alias.indexing():
            my_indexer.reindex()

        expect(MyDocType.search().count()).to.equal(3)
        expect(MyDocType.search().query('term', id=1).execute()[0].to_dict()['value']).to.equal(11)
        expect(MyDocType.search().query('term', id=2).execute()[0].to_dict()['value']).to.equal(12)
        expect(MyDocType.search().query('term', id=3).execute()[0].to_dict()['value']).to.equal(3)

    def test_create_mapping(self):
        @my_index_alias.doc_type
        class MyDocType2(DocType):
            value2 = Float()

            class Meta:
                doc_type = 'my_doc_type_2'

        @register_indexer('my_alias')
        class MyIndexer(BaseIndexer):
            doc_type_klass = MyDocType
            index_alias = my_index_alias

        @register_indexer('my_alias')
        class MyIndexer2(BaseIndexer):
            doc_type_klass = MyDocType2
            index_alias = my_index_alias

        class MyPartialIndexer(PartialIndexer, MyIndexer):
            batch_size = 2

            def get_batch_queryset(self, keys):
                return Mock(
                    count=Mock(return_value=len(keys)),
                    __iter__=Mock(return_value=iter([Mock(id=key, value=key + 10) for key in keys]))
                )

            def get_batch_update_docs_queries(self, keys):
                return self.doc_type_klass.search().query('terms', id=keys)

            def extract_datum(self, datum):
                return {'id': datum.id, 'value': datum.value}

            def get_postgres_count(self, keys):
                return len(keys)

        for value in [1, 2, 3]:
            MyDocType(id=value, value=value).save()
            MyDocType2(id=value, value2=value).save()
        my_index_alias.read_index.refresh()

        my_indexer = MyPartialIndexer(updating_keys=[1, 2])
        with my_indexer.index_alias.indexing():
            my_indexer.reindex()

        expect(MyDocType.search().count()).to.equal(3)
        expect(MyDocType.search().query('term', id=1).execute()[0].to_dict()['value']).to.equal(11)
        expect(MyDocType.search().query('term', id=2).execute()[0].to_dict()['value']).to.equal(12)
        expect(MyDocType.search().query('term', id=3).execute()[0].to_dict()['value']).to.equal(3)

        expect(MyDocType2.search().count()).to.equal(3)
        expect(MyDocType2.search().query('term', id=1).execute()[0].to_dict()['value2']).to.equal(1)
        expect(MyDocType2.search().query('term', id=2).execute()[0].to_dict()['value2']).to.equal(2)
        expect(MyDocType2.search().query('term', id=3).execute()[0].to_dict()['value2']).to.equal(3)

        expect(Mapping.from_es('test_my_alias', 'my_doc_type').to_dict()).to.eq({
            'my_doc_type': {
                'properties': {
                    'id': {'type': 'keyword'},
                    'value': {'type': 'float'}
                }
            }
        })

        expect(Mapping.from_es('test_my_alias', 'my_doc_type_2').to_dict()).to.eq({
            'my_doc_type_2': {
                'properties': {
                     'id': {'type': 'keyword'},
                     'value2': {'type': 'float'}
                 }
            }
        })
