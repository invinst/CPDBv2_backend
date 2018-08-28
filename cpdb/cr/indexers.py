from datetime import datetime

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.constants import GENDER_DICT, FINDINGS_DICT
from .doc_types import CRDocType
from .queries import AllegationQuery
from .index_aliases import cr_index_alias

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias
    query = AllegationQuery()

    def __init__(self, query=None, *args, **kwargs):
        super(CRIndexer, self).__init__(*args, **kwargs)
        if query is not None:
            self.query = query

    def get_queryset(self):
        return self.query.execute()

    def extract_datum(self, datum):
        def get_abbr_name(obj):
            return '. '.join([obj['first_name'][0].upper(), obj['last_name']])

        def get_full_name(obj):
            return ' '.join([obj['first_name'], obj['last_name']])

        def get_date(obj):
            return obj.strftime('%Y-%m-%d') if obj is not None else None

        def get_gender(obj):
            return GENDER_DICT.get(obj, None)

        def get_address(obj):
            if obj['old_complaint_address'] is not None:
                return obj['old_complaint_address']
            result = ' '.join(filter(None, [obj['add1'], obj['add2']]))
            return ', '.join(filter(None, [result, obj['city']]))

        result = {
            'crid': datum['crid'],
            'most_common_category': None,
            'coaccused': [],
            'summary': datum['summary'],
            'point': {'lon': datum['point'].x, 'lat': datum['point'].y} if datum['point'] is not None else None,
            'incident_date': get_date(datum['incident_date']),
            'start_date': None,
            'end_date': None,
            'address': get_address(datum),
            'location': datum['location'],
            'beat': datum['beat'],
            'involvements': [],
        }
        category_count = dict()
        category_names = set()

        for accused in datum['coaccused']:
            category = category_count.setdefault(accused['category_id'], {
                'allegation_name': accused['allegation_name'],
                'category': accused['category'],
                'count': 0
            })
            category['count'] += 1
            category_names.add(accused['category'])
            if accused['start_date'] is not None and result['start_date'] is None:
                result['start_date'] = accused['start_date'].strftime('%Y-%m-%d')
            if accused['end_date'] is not None and result['end_date'] is None:
                result['end_date'] = accused['end_date'].strftime('%Y-%m-%d')
            result['coaccused'].append({
                'id': accused['id'],
                'full_name': get_full_name(accused),
                'abbr_name': get_abbr_name(accused),
                'gender': get_gender(accused['gender']),
                'race': accused['race'],
                'rank': accused['rank'],
                'final_outcome': accused['final_outcome'],
                'final_finding': FINDINGS_DICT.get(accused['final_finding'], None),
                'recc_outcome': accused['recc_outcome'],
                'category': accused['category'],
                'subcategory': accused['allegation_name'],
                'start_date': get_date(accused['start_date']),
                'end_date': get_date(accused['end_date']),
                'age': datetime.now().year - accused['birth_year'] if accused['birth_year'] is not None else None,
                'allegation_count': accused['allegation_count'],
                'sustained_count': accused['sustained_count'],
                'disciplined': accused['disciplined'],
                'percentile_allegation': accused['complaint_percentile'],
                'percentile_allegation_civilian': accused['civilian_allegation_percentile'],
                'percentile_allegation_internal': accused['internal_allegation_percentile'],
                'percentile_trr': accused['trr_percentile'],
            })

        result['category_names'] = list(category_names)
        try:
            result['most_common_category'] = max(category_count.values(), key=lambda obj: obj['count'])
            result['most_common_category'].pop('count')
        except ValueError:
            pass

        result['complainants'] = [
            {
                'gender': get_gender(obj['gender']),
                'race': obj['race'],
                'age': obj['age']
            }
            for obj in datum['complainants']
        ]

        result['victims'] = [
            {
                'gender': get_gender(obj['gender']),
                'race': obj['race'],
                'age': obj['age']
            }
            for obj in datum['victims']
        ]

        def get_investigator_full_name(obj):
            if obj['officer_first_name'] is not None:
                return ' '.join(filter(None, [obj['officer_first_name'], obj['officer_last_name']]))
            return ' '.join(filter(None, [obj['investigator_first_name'], obj['investigator_last_name']]))

        def get_investigator_abbr_name(obj):
            if obj['officer_first_name'] is not None and obj['officer_last_name'] is not None:
                return '. '.join([obj['officer_first_name'][0].upper(), obj['officer_last_name']])
            elif obj['investigator_first_name'] is not None and obj['investigator_last_name'] is not None:
                return '. '.join([obj['investigator_first_name'][0].upper(), obj['investigator_last_name']])
            return None

        result['involvements'] = [
            {
                'officer_id': obj['officer_id'],
                'involved_type': 'investigator',
                'full_name': get_investigator_full_name(obj),
                'abbr_name': get_investigator_abbr_name(obj),
                'percentile_allegation': obj['complaint_percentile'],
                'percentile_allegation_civilian': obj['civilian_allegation_percentile'],
                'percentile_allegation_internal': obj['internal_allegation_percentile'],
                'percentile_trr': obj['trr_percentile'],
                'num_cases': obj['num_cases'],
                'current_rank': obj['current_rank'],
            }
            for obj in datum['investigators']
        ]

        result['involvements'] += [
            {
                'officer_id': obj['officer_id'],
                'involved_type': 'police_witness',
                'full_name': get_full_name(obj),
                'abbr_name': get_abbr_name(obj),
                'allegation_count': obj['allegation_count'],
                'sustained_count': obj['sustained_count'],
                'gender': get_gender(obj['gender']),
                'race': obj['race'],
                'percentile_allegation': obj['complaint_percentile'],
                'percentile_allegation_civilian': obj['civilian_allegation_percentile'],
                'percentile_allegation_internal': obj['internal_allegation_percentile'],
                'percentile_trr': obj['trr_percentile'],
            }
            for obj in datum['police_witnesses']
        ]

        result['attachments'] = [
            {
                'title': obj['title'],
                'url': obj['url'],
                'preview_image_url': obj['preview_image_url'],
                'file_type': obj['file_type']
            }
            for obj in datum['attachments']
        ]

        return result
