from django.test import TestCase

from elasticsearch_dsl import DocType
from mock import Mock
from robber import expect

from es_index import es_client
from es_index.index_aliases import IndexAlias
from es_index.indices import Index


class IndexAliasTestCase(TestCase):
    name = 'abc'
    real_name = 'test_abc'
    alias = IndexAlias(name)
    old_read_index = Index('old')

    @alias.doc_type
    class TestDocType(DocType):
        pass

    def setUp(self):
        es_client.indices.delete(self.real_name, ignore=404)
        self.old_read_index.delete(ignore=404)
        self.old_read_index.create()
        es_client.indices.put_alias(self.old_read_index._name, self.real_name)

    def test_indexing(self):
        expect(self.old_read_index.exists()).to.be.true()

        expect(self.alias.name).to.eq(self.real_name)
        expect(self.alias.new_index_name).to.ne(self.real_name)

        with self.alias.indexing():
            doc = self.TestDocType(a='b')
            doc.save(index=self.alias.new_index_name)

        self.alias.read_index.refresh()
        self.alias.write_index.refresh()

        expect(self.old_read_index.exists()).to.be.false()
        expect(doc._doc_type.index).to.eq(self.real_name)
        expect(self.TestDocType.search().count()).to.eq(1)
        expect(self.alias.write_index.search().count()).to.eq(1)

    def test_querying(self):
        self.TestDocType(c='d').save()
        self.old_read_index.refresh()
        expect(self.TestDocType.search().count()).to.eq(1)
        expect(self.old_read_index.search().count()).to.eq(1)

    def test_remove_write_index_if_exception(self):
        class MyException(Exception):
            pass

        def indexing():
            with self.alias.indexing():
                expect(self.alias.write_index.exists()).to.be.true()
                raise MyException()

        expect(indexing).to.throw_exactly(MyException)
        expect(self.alias.write_index.exists()).to.be.false()

    def test_migrate_not_call_reindex_when_doc_types_empty(self):
        es_client.reindex = Mock()
        self.alias.migrate([])
        expect(es_client.reindex).not_to.be.called()

    def test_migrate_call_reindex_when_doc_types_is_not_empty(self):
        es_client.reindex = Mock()
        self.alias.write_index.open = Mock()
        self.alias.migrate(['type1'])
        expect(self.alias.write_index.open).to.be.called()
        expect(es_client.reindex).to.be.called_with({
            'dest': {'index': self.alias.new_index_name, 'version_type': 'external'},
            'source': {'index': 'test_abc', 'type': ['type1']},
        }, request_timeout=300)
