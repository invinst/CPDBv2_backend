from data.models import Officer
from .doc_types import OfficerDocType


class ElasticSearchOfficerExtractor:
    def get_officers(self, names):
        results = []
        seen_ids = []
        for (source, name) in names:
            query = OfficerDocType().search().query(
                'function_score',
                query={
                    'match': {
                        'name': {
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
            results += [
                (source, Officer.objects.get(pk=obj['id']))
                for obj in search_result if obj['id'] not in seen_ids]
            seen_ids += [obj['id'] for obj in search_result]

        return results
