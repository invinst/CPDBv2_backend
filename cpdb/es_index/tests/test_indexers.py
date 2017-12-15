from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from es_index.indexers import BaseIndexer


class IndexersTestCase(SimpleTestCase):
    def test_get_queryset(self):
        expect(lambda: BaseIndexer().get_queryset()).to.throw(NotImplementedError)

    def test_extract_datum(self):
        expect(lambda: BaseIndexer().extract_datum('anything')).to.throw(NotImplementedError)

    def test_index_datum(self):
        indexer = BaseIndexer()
        doc_type = Mock()
        indexer.doc_type_klass = Mock(return_value=doc_type)
        indexer.extract_datum = Mock(return_value={'key': 'something'})
        indexer.get_queryset = Mock(return_value=['something'])
        indexer.index_alias = Mock()

        indexer.index_datum('anything')

        indexer.doc_type_klass.assert_called_once_with(key='something')
        expect(doc_type.save.called).to.be.true()

    def test_index_datum_return_generator(self):
        def extract_datum(*args):
            yield {'key': 'something'}

        indexer = BaseIndexer()
        doc_type = Mock()
        indexer.doc_type_klass = Mock(return_value=doc_type)
        indexer.extract_datum = extract_datum
        indexer.get_queryset = Mock(return_value=['something'])
        indexer.index_alias = Mock()

        indexer.index_datum('anything')

        indexer.doc_type_klass.assert_called_once_with(key='something')
        expect(doc_type.save.called).to.be.true()

    def test_reindex(self):
        indexer = BaseIndexer()
        indexer.get_queryset = Mock(return_value=[1])
        indexer.doc_type_klass = Mock()
        indexer.index_datum = Mock()
        indexer.index_alias = Mock()

        indexer.reindex()

        indexer.index_datum.assert_called_once_with(1)
