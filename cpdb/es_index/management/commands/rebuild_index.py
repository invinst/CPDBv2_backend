from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

from es_index import indexer_klasses, indexer_klasses_map, es_client


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*')

    def get_indexers(self, **options):
        autodiscover_modules('indexers')

        indexers = []
        if len(options['app']):
            for app in options['app']:
                app_split = app.split('.')
                if len(app_split) == 1:
                    indexers = indexers + list(indexer_klasses_map[app])
                else:
                    for indexer in indexer_klasses_map[app_split[0]]:
                        if indexer.doc_type_klass._doc_type.name == app_split[1]:
                            indexers.append(indexer)
        else:
            indexers = indexer_klasses
        return indexers

    def categorize_indexers_by_index_alias(self, indexers):
        indexers_map = dict()
        alias_map = dict()
        for indexer in indexers:
            indexers_map.setdefault(indexer.index_alias.name, []).append(indexer)
            alias_map[indexer.index_alias.name] = indexer.index_alias

        return [(
            alias_map[key],
            indexers_map[key],
            list(indexer_klasses_map[key] - set(indexers_map[key]))
        ) for key in alias_map.keys()]

    def _get_distinct_doc_types_from_indexers(self, indexers):
        return list(set(x.doc_type_klass._doc_type.name for x in indexers))

    def _migrate(self, index_alias, migrate_doc_types=[]):
        if not migrate_doc_types:
            return

        index_alias.write_index.open()
        query = {}
        query['source'] = {'index': index_alias.name, 'type': migrate_doc_types}
        query['dest'] = {
            'index': index_alias.new_index_name,
            'version_type': 'external'
        }
        es_client.reindex(query)

    def handle(self, *args, **options):
        selected_indexers = self.get_indexers(**options)
        alias_indexers_tuple = self.categorize_indexers_by_index_alias(selected_indexers)

        for alias, indexers, migrating_indexers in alias_indexers_tuple:
            with alias.indexing():

                list_migrate_doc_types = self._get_distinct_doc_types_from_indexers(migrating_indexers)
                indexer_klass_instances = [klass() for klass in indexers]
                for indexer_instance in indexer_klass_instances:
                    indexer_instance.create_mapping()
                self._migrate(alias, list_migrate_doc_types)

                for indexer_instance in indexer_klass_instances:
                    indexer_instance.add_new_data()
