from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch


es_client = Elasticsearch(hosts=['localhost:9200'])

connections.add_connection('default', es_client)

indexer_klasses = set()
index_klasses = set()


def register_indexer(klass):
    indexer_klasses.add(klass)
    return klass


def register_index(index):
    index_klasses.add(index)
    return index
