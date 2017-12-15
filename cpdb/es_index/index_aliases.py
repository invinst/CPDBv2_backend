from contextlib import contextmanager

from django.conf import settings

from . import es_client
from .indices import Index
from .utils import per_run_uuid


class IndexAlias:
    def __init__(self, name):
        self.name = name
        self.new_index_name = '%s_%s' % (name, per_run_uuid)
        self._read_index = Index(name)
        self._write_index = Index(self.new_index_name)
        if getattr(settings, 'TEST', False):
            self.new_index_name = 'test_%s' % self.new_index_name
            self.name = 'test_%s' % self.name

    def doc_type(self, doc_type):
        return self._read_index.doc_type(doc_type)

    def close_write_index(self):
        self._write_index.close()

    def open_write_index(self):
        self._write_index.open()

    @contextmanager
    def indexing(self):
        self._write_index.create(ignore=400)
        try:
            yield self
        except Exception:
            self._write_index.delete(ignore=404)
            raise
        self._read_index.delete(ignore=404)
        es_client.indices.put_alias(index=self.new_index_name, name=self.name)
