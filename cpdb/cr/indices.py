from es_index import register_index
from es_index.indices import Index


app_name = __name__.split('.')[0]
cr_index = register_index(app_name)(Index('cr'))
