from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

from es_index import indexer_klasses, indexer_klasses_map


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*')

    def get_indexers(self, **options):
        autodiscover_modules('indexers')

        indexers = []
        if len(options['app']):
            for app in options['app']:
                indexers = indexers + list(indexer_klasses_map[app])
        else:
            indexers = indexer_klasses
        return indexers

    def categorize_indexers_by_index_alias(self, indexers):
        indexers_map = dict()
        alias_map = dict()
        for indexer in indexers:
            indexers_map.setdefault(indexer.index_alias.name, []).append(indexer)
            alias_map[indexer.index_alias.name] = indexer.index_alias
        return [(alias_map[key], indexers_map[key]) for key in alias_map.keys()]

    def handle(self, *args, **options):
        selected_indexers = self.get_indexers(**options)
        alias_indexers_tuple = self.categorize_indexers_by_index_alias(selected_indexers)

        for alias, indexers in alias_indexers_tuple:
            with alias.indexing():
                for indexer_klass in indexers:
                    indexer_klass().reindex()
