import types
from elasticsearch import NotFoundError

from tqdm import tqdm
from elasticsearch.helpers import bulk

from es_index import es_client


class BaseIndexer(object):
    doc_type_klass = None
    index_alias = None
    parent_doc_type_property = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def doc_dict(self, raw_doc):
        doc = self.doc_type_klass(**raw_doc).to_dict(include_meta=True)
        doc['_op_type'] = 'create'
        doc['_index'] = self.index_alias.new_index_name
        return doc

    def docs(self, to_dict=True):
        for datum in tqdm(
                self.get_queryset(),
                desc='Indexing {doc_type_name}({indexer_name})'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name,
                    indexer_name = self.__class__.__name__
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
        if not self.parent_doc_type_property:
            raise TypeError('parent_doc_type_property must be set if parent_doc_type is not null')
        for doc in docs:
            # NOTE: current `id` must be matched with parent indexer `id`
            try:
                saved_doc = self.doc_type_klass.get(id=doc['id'], index=self.index_alias.new_index_name)
                update_field = getattr(saved_doc, self.parent_doc_type_property)._l_
                update_field.append(doc)
                saved_doc.update(**{self.parent_doc_type_property: update_field})
            except NotFoundError:
                pass
                # print 'Can not found officer with id {}'.format(doc['id'])

    def add_new_data(self):
        self.index_alias.write_index.settings(refresh_interval='-1')
        self.index_alias.write_index.open()
        if self.parent_doc_type_property:
            self.upsert(self.docs(to_dict=False))
        else:
            bulk(es_client, self.docs())
        self.index_alias.write_index.settings(refresh_interval='1s')

    def reindex(self):
        self.create_mapping()
        self.add_new_data()
