from tqdm import tqdm


class BaseIndexer(object):
    doc_type_klass = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def index_datum(self, datum):
        doc = self.doc_type_klass(**self.extract_datum(datum))
        doc.save()

    def reindex(self):
        for datum in tqdm(
                self.get_queryset(),
                desc='Indexing {doc_type_name}'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name)):
            self.index_datum(datum)
