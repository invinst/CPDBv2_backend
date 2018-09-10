import copy
import types

from django.utils.module_loading import autodiscover_modules

from tqdm import tqdm
from elasticsearch.helpers import bulk

from es_index import es_client
from es_index import indexer_klasses


class BaseIndexer(object):
    doc_type_klass = None
    index_alias = None
    parent_doc_type_property = None
    op_type = 'index'

    def _embed_update_script(self, doc):
        raw_doc = copy.deepcopy(doc['_source'])
        doc['_op_type'] = 'update'
        if self.parent_doc_type_property:
            doc['_source'] = {
                'upsert': {
                    "id": raw_doc['id'],
                    self.parent_doc_type_property: [raw_doc]
                }
            }
            doc['_source']['script'] = {
                "inline": "if (!ctx._source.containsKey('{property}')) {{ ctx._source.{property} = [] }} "
                          "ctx._source.{property}.add(params.new_doc)".format(property=self.parent_doc_type_property),
                "lang": "painless",
                "params": {"new_doc": raw_doc}
            }
        else:
            raw_doc.pop('id', None)
            doc['_source'] = {'doc': raw_doc}
        return doc

    def doc_dict(self, raw_doc):
        doc = self.doc_type_klass(**raw_doc).to_dict(include_meta=True)
        doc['_index'] = self.index_alias.new_index_name
        doc['_op_type'] = self.op_type

        if 'id' in raw_doc:
            doc['_id'] = raw_doc['id']

        # if op_type is update, we update instead of creating
        if self.parent_doc_type_property or self.op_type == 'update':
            doc = self._embed_update_script(doc)
        return doc

    def get_objects(self):
        if hasattr(self, 'get_query'):
            return self.get_query()
        return self.get_queryset()

    def docs(self):
        for datum in tqdm(
                self.get_objects(),
                desc='Indexing {doc_type_name}({indexer_name})'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name,
                    indexer_name=self.__class__.__name__
                )):
            result = self.extract_datum(datum)
            if isinstance(result, types.GeneratorType):
                for obj in result:
                    yield self.doc_dict(obj)
            else:
                yield self.doc_dict(result)

    def create_mapping(self):
        self.index_alias.write_index.close()
        if not self.parent_doc_type_property:
            self.doc_type_klass.init(index=self.index_alias.new_index_name)

    def add_new_data(self):
        self.index_alias.write_index.settings(refresh_interval='-1')
        self.index_alias.write_index.open()
        bulk(es_client, self.docs())
        self.index_alias.write_index.settings(refresh_interval='1s')
        self.index_alias.write_index.refresh()

    def reindex(self):
        self.create_mapping()
        self.add_new_data()


class PartialIndexer(BaseIndexer):
    batch_size = 1000

    def __init__(self, updating_keys=None):
        super(PartialIndexer, self).__init__()
        self.updating_keys = list(updating_keys) if updating_keys else []

    def create_mapping(self):
        self.index_alias.write_index.close()
        autodiscover_modules('indexers')
        doc_types = [indexer.doc_type_klass for indexer in indexer_klasses if indexer.index_alias == self.index_alias]
        for doc_type in doc_types:
            doc_type.init(index=self.index_alias.new_index_name)

    def reindex(self):
        self.validate_updated_docs()
        self.create_mapping()
        self.index_alias.migrate()
        self.delete_existing_docs()
        self.add_new_data()

    def get_keys_batches(self):
        for i in range(0, len(self.updating_keys), self.batch_size):
            yield self.updating_keys[i:i + self.batch_size]

    def get_batch_queryset(self, keys):
        raise NotImplementedError

    def get_batch_update_docs_queries(self, keys):
        raise NotImplementedError

    @property
    def batch_querysets(self):
        for keys_batch in self.get_keys_batches():
            yield self.get_batch_queryset(keys_batch)

    @property
    def batch_postgres_count(self):
        for keys_batch in self.get_keys_batches():
            yield self.get_postgres_count(keys_batch)

    @property
    def batch_update_docs_queries(self):
        for keys_batch in self.get_keys_batches():
            yield self.get_batch_update_docs_queries(keys_batch)

    def get_queryset(self):
        for queryset in self.batch_querysets:
            for item in queryset:
                yield item

    def delete_existing_docs(self):
        self.index_alias.write_index.open()
        for update_docs_query in self.batch_update_docs_queries:
            es_client.delete_by_query(
                index=self.index_alias.new_index_name,
                body=update_docs_query.to_dict(),
                doc_type=self.doc_type_klass._doc_type.name)

        self.index_alias.write_index.refresh()

    def validate_updated_docs(self):
        num_es_docs = sum(update_docs_query.count() for update_docs_query in self.batch_update_docs_queries)
        num_postgres_rows = sum(self.batch_postgres_count)

        if num_postgres_rows != num_es_docs:
            raise ValueError(
                (
                    'Can not update index for %s. '
                    'Number of ES doc (%d) is not equal to number of PostgreS rows (%d)'
                ) % (
                    self.doc_type_klass._doc_type.name, num_es_docs, num_postgres_rows
                )
            )
