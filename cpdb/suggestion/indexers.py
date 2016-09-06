import re

from tqdm import tqdm

from suggestion.doc_types import AutoComplete
from suggestion.indexes import autocompletes
from suggestion.autocomplete_types import AutoCompleteType
from data.models import Officer
from data.constants import FINDINGS, AREA_CHOICES
from es_index import register_indexer

FINDINGS_DICT = dict(FINDINGS)
AREA_CHOICES_DICT = dict(AREA_CHOICES)


@register_indexer
class AutoCompleteIndexer(object):
    def clear_index(self):
        autocompletes.delete(ignore=404)

    def reindex(self):
        self.clear_index()
        AutoComplete.init()
        self._index_officer_name()

    def _prefix_tokenize(self, input):
        words = re.split(r'[^a-zA-Z0-9]+', input)
        len_words = len(words)
        for ind in xrange(len_words):
            if len_words - ind > 10:
                stop_ind = ind + 10
            else:
                stop_ind = len_words
            yield ' '.join(words[ind:stop_ind])

    def _index_officer_name(self):
        for officer in tqdm(Officer.objects.all(), desc='Indexing autocomplete officer names'):
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(officer.full_name)),
                    'output': officer.full_name,
                    'payload': {
                        'type': AutoCompleteType.OFFICER_NAME,
                        'url': officer.relative_url
                    }
                })
            doc.save()
