from django.conf import settings

from elasticsearch_dsl import Index as BaseIndex


class Index(BaseIndex):
    def __init__(self, index_name, *args, **kwargs):
        if getattr(settings, 'TEST', False):
            super(Index, self).__init__(f'test_{index_name}', *args, **kwargs)
            self.settings(number_of_shards=10, number_of_replicas=0)
        else:
            super(Index, self).__init__(index_name, *args, **kwargs)  # pragma: no cover
