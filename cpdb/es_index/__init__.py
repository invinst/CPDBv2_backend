from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost:9200'])
