from sets import Set

from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch


es_client = Elasticsearch(hosts=['localhost:9200'])

connections.add_connection('default', es_client)

indexers = Set([])


def register_indexer(klass):
    indexers.add(klass)
    return klass
