from django.conf import settings

from elasticsearch_dsl import Index as BaseIndex

from .analyzers import autocomplete, autocomplete_search


class Index(BaseIndex):
    def __init__(self, index_name, *args, **kwargs):
        if getattr(settings, 'TEST', False):
            super(Index, self).__init__('test_%s' % index_name, *args, **kwargs)
            self.settings(number_of_shards=1, number_of_replicas=0)
        else:
            super(Index, self).__init__(index_name, *args, **kwargs)  # pragma: no cover


autocompletes = Index('autocompletes')
autocompletes.analyzer(autocomplete)
autocompletes.analyzer(autocomplete_search)
