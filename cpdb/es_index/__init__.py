from django.conf import settings

from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch


es_client = Elasticsearch(hosts=settings.ELASTICSEARCH_HOSTS, timeout=300)

connections.add_connection('default', es_client)

indexer_klasses = []
indexer_klasses_map = dict()


def register_indexer(app):
    def func(klass):
        indexer_klasses.append(klass)
        indexer_klasses_map.setdefault(app, []).append(klass)
        return klass
    return func
