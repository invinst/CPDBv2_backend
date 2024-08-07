import copy
import types

from elasticsearch.helpers import bulk
from tqdm import tqdm

from es_index import es_client


class BaseIndexer(object):
    doc_type_klass = None
    index_alias = None
    parent_doc_type_property = None
    op_type = 'index'

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

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
            property = self.parent_doc_type_property
            doc['_source']['script'] = {
                'inline': f"if (!ctx._source.containsKey('{property}')) {{ ctx._source.{property} = [] }} "
                          f'ctx._source.{property}.add(params.new_doc)',
                'lang': 'painless',
                'params': {'new_doc': raw_doc}
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

    def docs(self):
        for datum in tqdm(
            self.get_queryset(),
            desc=f'Indexing {self.doc_type_klass._doc_type.name}({self.__class__.__name__})'
        ):
            result = self.extract_datum(datum)
            if isinstance(result, types.GeneratorType):
                for obj in result:
                    yield self.doc_dict(obj)
            else:
                yield self.doc_dict(result)

    @classmethod
    def create_mapping(cls):
        cls.index_alias.write_index.close()
        if not cls.parent_doc_type_property:
            cls.doc_type_klass.init(index=cls.index_alias.new_index_name)

    def add_new_data(self):
        self.index_alias.write_index.settings(refresh_interval='-1')
        self.index_alias.write_index.open()
        bulk(es_client, self.docs())
        self.index_alias.write_index.settings(refresh_interval='1s')
        self.index_alias.write_index.refresh()

    def reindex(self):
        self.create_mapping()
        self.add_new_data()
