from django.core.management.base import BaseCommand

from search.search_indexers import IndexerManager
from search.constants import DEFAULT_INDEXERS


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        IndexerManager(indexers=DEFAULT_INDEXERS).rebuild_index()
