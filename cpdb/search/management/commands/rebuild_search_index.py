import json

from django.core.management.base import BaseCommand

from search.search_indexers import IndexerManager
from search.constants import DEFAULT_INDEXERS


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*')
        parser.add_argument(
            '--from-file',
            dest='from_file',
            help='Read config json and choose which type to rebuild'
        )

    def get_doc_types_from_json(self, file_name):
        with open(file_name) as f:
            return json.load(f)

    def _get_indexers(self, options):
        if len(options['app']):
            doc_types = options['app']
        elif options['from_file']:
            doc_types = self.get_doc_types_from_json(options['from_file'])
        else:
            return DEFAULT_INDEXERS
        return [idx for idx in DEFAULT_INDEXERS
                if idx.doc_type_klass._doc_type.name in doc_types]

    def _get_migrate_doc_types(self, indexers):
        return [idx.doc_type_klass._doc_type.name
                for idx in (set(DEFAULT_INDEXERS) - set(indexers))]

    def handle(self, *args, **kwargs):
        indexers = self._get_indexers(kwargs)
        migrate_doc_types = self._get_migrate_doc_types(indexers)
        IndexerManager(indexers).rebuild_index(migrate_doc_types)
