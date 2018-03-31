import types

from tqdm import tqdm
from elasticsearch.helpers import bulk
from elasticsearch import NotFoundError

from es_index import es_client


class BaseIndexer(object):
    doc_type_klass = None
    index_alias = None
    parent_doc_type_property = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def _embed_update_script(self, doc):
        raw_doc = doc['_source']
        doc['_op_type'] = 'update'
        doc['_source'] = {
            'upsert': {
                "id": raw_doc['id'],
                "percentiles": [raw_doc]
            }
        }
        doc['_source']['script'] = {
            "inline": "if (!ctx._source.containsKey('{property}')) {{ ctx._source.{property} = [] }} "
                      "ctx._source.{property}.add(params.new_doc)".format(property=self.parent_doc_type_property),
            "lang": "painless",
            "params": {"new_doc": raw_doc}
        }
        return doc

    def doc_dict(self, raw_doc):
        doc = self.doc_type_klass(**raw_doc).to_dict(include_meta=True)
        doc['_index'] = self.index_alias.new_index_name
        doc['_op_type'] = 'create'

        # if this is children indexers, we update instead of creating
        if self.parent_doc_type_property:
            # use script with bulk MUCH faster than get-save method (8min < 35min)
            doc['_id'] = raw_doc['id']
            doc = self._embed_update_script(doc)
        return doc

    def docs(self, to_dict=True):
        for datum in tqdm(
                self.get_queryset(),
                desc='Indexing {doc_type_name}({indexer_name})'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name,
                    indexer_name=self.__class__.__name__
                )):
            result = self.extract_datum(datum)
            if isinstance(result, types.GeneratorType):
                for obj in result:
                    yield self.doc_dict(obj) if to_dict else obj
            else:
                yield self.doc_dict(result) if to_dict else result

    def create_mapping(self):
        self.index_alias.write_index.close()
        if not self.parent_doc_type_property:
            self.doc_type_klass.init(index=self.index_alias.new_index_name)

    def upsert(self, docs):
        """ This function will read docs from `docs(no_dict=False)`, then get the document, read content
        update new elements, then write it.
        NOTE: This is SO SLOW, so we not use this, but use bulk updating by painless-scripting
        """
        if not self.parent_doc_type_property:
            raise TypeError('parent_doc_type_property must be set if parent_doc_type is not null')
        for doc in docs:
            try:
                # NOTE: current `id` must be matched with parent indexer `id`
                saved_doc = self.doc_type_klass.get(id=doc['id'], index=self.index_alias.new_index_name)
                getattr(saved_doc, self.parent_doc_type_property).append(doc)
                saved_doc.save()
            except NotFoundError:  # should create here
                pass

    def add_new_data(self):
        self.index_alias.write_index.settings(refresh_interval='-1')
        self.index_alias.write_index.open()
        bulk(es_client, self.docs())
        self.index_alias.write_index.settings(refresh_interval='1s')

    def reindex(self):
        self.create_mapping()
        self.add_new_data()
