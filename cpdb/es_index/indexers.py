import re

from tqdm import tqdm

from es_index.doc_types import AutoComplete
from es_index.indexes import autocompletes
from es_index.autocomplete_types import AutoCompleteType
from data.models import Officer, OfficerAllegation, Area, Allegation
from data.constants import FINDINGS, AREA_CHOICES

FINDINGS_DICT = dict(FINDINGS)
AREA_CHOICES_DICT = dict(AREA_CHOICES)


class AutoCompleteIndexer(object):
    def clear_index(self):
        autocompletes.delete(ignore=404)

    def reindex(self):
        self.clear_index()
        AutoComplete.init()
        self._index_officer_name()
        self._index_final_finding()
        self._index_area()
        self._index_allegation_summary()

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
            output = '%s %s' % (officer.first_name, officer.last_name)
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(output)),
                    'output': output,
                    'payload': {
                        'type': AutoCompleteType.OFFICER_NAME,
                        'url': officer.relative_url
                    }
                })
            doc.save()

    def _index_final_finding(self):
        for oa in tqdm(
                OfficerAllegation.objects.values('final_finding').distinct(),
                desc='Indexing autocomplete final finding'):
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(FINDINGS_DICT[oa['final_finding']])),
                    'output': FINDINGS_DICT[oa['final_finding']],
                    'payload': {
                        'type': AutoCompleteType.FINAL_FINDING,
                        'value': oa['final_finding']
                    }
                })
            doc.save()

    def _index_area(self):
        for area in tqdm(Area.objects.all(), desc='Indexing autocomplete area'):
            output = '%s: %s' % (AREA_CHOICES_DICT[area.area_type], area.name)
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(output)),
                    'output': output,
                    'payload': {
                        'type': AutoCompleteType.AREA,
                        'value': area.pk
                    }
                })
            doc.save()

    def _index_allegation_summary(self):
        for allegation in tqdm(
                Allegation.objects.filter(summary__isnull=False).exclude(summary=''),
                desc='Indexing autocomplete allegation summary'):
            doc = AutoComplete(
                suggest={
                    'input': list(self._prefix_tokenize(allegation.summary)),
                    'output': 'CRID %s' % allegation.crid,
                    'payload': {
                        'type': AutoCompleteType.ALLEGATION_SUMMARY,
                        'value': allegation.pk,
                        'text': allegation.summary
                    }
                })
            doc.save()
