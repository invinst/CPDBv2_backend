from django.conf import settings

from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch


es_client = Elasticsearch(hosts=settings.ELASTICSEARCH_HOSTS)

connections.add_connection('default', es_client)
