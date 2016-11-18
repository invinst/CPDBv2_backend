import re

from tqdm import tqdm

from suggestion.doc_types import AutoComplete
from suggestion.indexes import autocompletes
from data.models import Officer, PoliceUnit, Area
from data.constants import FINDINGS, AREA_CHOICES
from es_index import register_indexer

FINDINGS_DICT = dict(FINDINGS)
AREA_CHOICES_DICT = dict(AREA_CHOICES)

AUTOCOMPLETE_MAPPING = (
    (Officer, 'officer names'),
    (PoliceUnit, 'police units'),
    (Area, 'areas')
)


@register_indexer
class AutoCompleteIndexer(object):
    def clear_index(self):
        autocompletes.delete(ignore=404)

    def reindex(self):
        self.clear_index()
        AutoComplete.init()
        self._index_autocomplete_mapping()

    def _prefix_tokenize(self, input):
        words = re.split(r'[^a-zA-Z0-9]+', input)
        len_words = len(words)
        for ind in xrange(len_words):
            if len_words - ind > 10:
                stop_ind = ind + 10
            else:
                stop_ind = len_words
            yield ' '.join(words[ind:stop_ind])

    def _index_autocomplete_mapping(self):
        for entry in AUTOCOMPLETE_MAPPING:
            self._index_autocompletes(*entry)

    def _index_autocompletes(self, model, desc):
        for datum in tqdm(model.objects.all(), desc='Indexing autocomplete %s' % desc):
            self._index_datum(datum)

    def _index_datum(self, datum):
        for (name, payload, context) in datum.index_args:
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(name)),
                    'output': name,
                    'payload': payload,
                    'context': context
                })
            doc.save()
