import json

from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

from es_index import indexer_klasses, indexer_klasses_map


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*')
        parser.add_argument(
            '--from-file',
            dest='from_file',
            help='Read config json and choose which indexer to rebuild'
        )

    def _get_indexer_names_from_json(self, file_name):
        with open(file_name) as f:
            return json.load(f)

    def _get_indexer_names_from_args(self, apps):
        indexer_names = {}

        for app in apps:
            app_split = app.split('.')
            indexer = app_split[0]
            es_type = app_split[1] if len(app_split) > 1 else None
            if len(app_split) == 1:
                indexer_names[indexer] = ['*']
            elif indexer not in indexer_names:
                indexer_names[indexer] = [es_type]
            else:
                indexer_names[indexer].append(es_type)
        return indexer_names

    def get_indexers(self, **options):
        autodiscover_modules('indexers')
        indexers = []
        if len(options['app']):
            indexer_names = self._get_indexer_names_from_args(options['app'])
        elif options['from_file']:
            indexer_names = self._get_indexer_names_from_json(options['from_file'])
        else:
            return indexer_klasses

        for indexer_name, doc_types in indexer_names.items():
            list_indexer = indexer_klasses_map[indexer_name]
            if '*' in doc_types:
                indexers += list(list_indexer)
                continue
            for doc_type in doc_types:
                indexers += [idx for idx in list_indexer
                             if idx.doc_type_klass._doc_type.name == doc_type]

        # Always ensure parent indexers to be index first
        indexers = sorted(indexers, key=lambda x: x.parent_doc_type_property)
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

    def handle(self, *args, **options):
        selected_indexers = self.get_indexers(**options)
        alias_indexers_tuple = self.categorize_indexers_by_index_alias(selected_indexers)

        for alias, indexers, migrating_indexers in alias_indexers_tuple:
            with alias.indexing():
                list_migrate_doc_types = self._get_distinct_doc_types_from_indexers(migrating_indexers)
                indexer_klass_instances = [klass() for klass in indexers]

                for indexer_instance in indexer_klass_instances:
                    indexer_instance.create_mapping()

                alias.migrate(list_migrate_doc_types)

                for indexer_instance in indexer_klass_instances:
                    indexer_instance.add_new_data()
