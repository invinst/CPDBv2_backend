from django.core.exceptions import ObjectDoesNotExist

from data.models import Officer
from .doc_types import OfficerDocType


class ElasticSearchOfficerExtractor:
    def _get_officer_id_from_name(self, name):
        query = OfficerDocType().search().query(
            'function_score',
            query={
                'match': {
                    'full_name': {
                        'query': name,
                        'operator': 'and'
                    }
                }
            },
            script_score={
                'script': {
                    'lang': 'painless',
                    'inline': '_score + doc[\'allegation_count\'].value * 3'
                }
            }
        )
        search_result = query[:1].execute()
        if not search_result:
            return None
        return search_result[0]['id']

    def _get_officer_from_id(self, officer_id):
        try:
            return Officer.objects.get(pk=officer_id)
        except ObjectDoesNotExist:
            return None

    def get_officers(self, names, ids=None):
        if ids:
            source_id_pairs = list(ids)
            all_ids = [officer_id for _, officer_id in ids]
        else:
            source_id_pairs = []
            all_ids = []

        for source, name in names:
            officer_id = self._get_officer_id_from_name(name)
            if officer_id is not None and officer_id not in all_ids:
                all_ids.append(officer_id)
                source_id_pairs.append((source, officer_id))

        results = []
        for source, officer_id in source_id_pairs:
            officer = self._get_officer_from_id(officer_id)
            if officer is not None:
                results.append((source, officer))

        return results
