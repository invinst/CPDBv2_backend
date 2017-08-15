from django.conf import settings

from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch


es_client = Elasticsearch(hosts=settings.ELASTICSEARCH_HOSTS)

connections.add_connection('default', es_client)

indexer_klasses = set()
indexer_klasses_map = dict()


def register_indexer(app):
    def func(klass):
        indexer_klasses.add(klass)
        indexer_klasses_map.setdefault(app, set()).add(klass)
        return klass
    return func
