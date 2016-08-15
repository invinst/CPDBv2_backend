from django.core.management import BaseCommand

from es_index.indexers import AutoCompleteIndexer


class Command(BaseCommand):
    def handle(self, *args, **options):
        AutoCompleteIndexer().reindex()
