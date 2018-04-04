import types

from tqdm import tqdm
from elasticsearch.helpers import bulk

from es_index import es_client


class BaseIndexer(object):
    doc_type_klass = None
    index_alias = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def doc_dict(self, raw_doc):
        doc = self.doc_type_klass(**raw_doc).to_dict(include_meta=True)
        doc['_index'] = self.index_alias.new_index_name
        return doc

    def docs(self):
        for datum in tqdm(
                self.get_queryset(),
                desc='Indexing {doc_type_name}'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name)):
            result = self.extract_datum(datum)
            if isinstance(result, types.GeneratorType):
                for obj in result:
                    yield self.doc_dict(obj)
            else:
                yield self.doc_dict(result)

    def create_mapping(self):
        self.index_alias.write_index.close()
        self.doc_type_klass.init(index=self.index_alias.new_index_name)

    def add_new_data(self):
        self.index_alias.write_index.settings(refresh_interval='-1')
        self.index_alias.write_index.open()
        bulk(es_client, self.docs())
        self.index_alias.write_index.settings(refresh_interval='1s')

    def reindex(self):
        self.create_mapping()
        self.add_new_data()
