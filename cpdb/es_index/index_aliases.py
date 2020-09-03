from contextlib import contextmanager

from django.conf import settings

from . import es_client
from .indices import Index
from .utils import per_run_uuid, timing_validate

REINDEX_TIMEOUT = 3600


class IndexAlias:
    def __init__(self, name):
        self.name = name
        self.new_index_name = f'{name}_{per_run_uuid}'
        self.read_index = Index(name)
        self.write_index = Index(self.new_index_name)
        if getattr(settings, 'TEST', False):
            self.new_index_name = f'test_{self.new_index_name}'
            self.name = f'test_{self.name}'

    def doc_type(self, doc_type):
        return self.read_index.doc_type(doc_type)

    @timing_validate('Start migrating...')
    def migrate(self, migrate_doc_types=None):
        if migrate_doc_types == []:
            return

        self.write_index.open()
        query = {
            'source': {'index': self.name},
            'dest': {'index': self.new_index_name, 'version_type': 'external'}
        }
        if migrate_doc_types is not None:
            query['source']['type'] = migrate_doc_types

        es_client.reindex(query, request_timeout=REINDEX_TIMEOUT, slices=10)
        self.write_index.refresh()

    @contextmanager
    def indexing(self):
        self.write_index.create(ignore=400)
        try:
            yield self
        except Exception:
            self.write_index.delete(ignore=404)
            raise
        self.read_index.delete(ignore=404)
        es_client.indices.put_alias(index=self.new_index_name, name=self.name)
        self.write_index.refresh()
