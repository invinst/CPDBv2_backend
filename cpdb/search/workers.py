from elasticsearch_dsl.query import Q

from .doc_types import UnitDocType, ReportDocType, AreaDocType, CrDocType, TRRDocType
from officers.doc_types import OfficerInfoDocType


class Worker(object):
    doc_type_klass = None
    fields = []
    sort_order = []
    name = ''
    search_with_dates = False

    @property
    def _searcher(self):
        return self.doc_type_klass().search()

    def query(self, term, **kwargs):
        return self._searcher \
            .query('multi_match', query=term, operator='and', fields=self.fields) \
            .sort(*self.sort_order)

    def search(self, term, size=10, begin=0, **kwargs):
        return self.query(term, **kwargs)[begin:size].execute()

    def get_sample(self):
        query = self._searcher.query(
            'function_score',
            random_score={}
        ).query(
            'exists',
            field='tags'
        )
        return query[:1].execute()


class ReportWorker(Worker):
    doc_type_klass = ReportDocType
    fields = ['excerpt', 'title', 'publication', 'author', 'tags']


class OfficerWorker(Worker):
    doc_type_klass = OfficerInfoDocType

    def query(self, term, **kwargs):
        _query = self._searcher.query(
            'function_score',
            query={
                'multi_match': {
                    'query': term,
                    'fields': ['badge', 'historic_badges', 'full_name', 'tags', '_id']
                }
            },
            functions=[
                {
                    'filter': {
                        'match': {
                            'tags': term
                        }
                    },
                    'script_score': {
                        'script': '_score + 60000'
                    }
                },
                {
                    'filter': {
                        'match': {
                            'full_name': {
                                'query': term,
                                'operator': 'and'
                            }
                        }
                    },
                    'script_score': {
                        'script': '_score + 500'
                    }
                },
                {
                    'filter': {
                        'match': {
                            'full_name': term
                        }
                    },
                    'script_score': {
                        'script': '_score + doc[\'allegation_count\'].value * 3'
                    }
                }
            ]
        )
        return _query


class UnitWorker(Worker):
    doc_type_klass = UnitDocType
    fields = ['name', 'description', 'tags']


class AreaWorker(Worker):
    doc_type_klass = AreaDocType
    area_type = None
    fields = ['name', 'tags']
    sort_order = ['-allegation_count', 'name.keyword', '_score']

    def query(self, term, **kwargs):
        filter = Q('term', area_type=self.area_type) if self.area_type else Q('match_all')
        q = Q('bool',
              must=[Q('multi_match', query=term, operator='and', fields=self.fields)],
              filter=filter)
        return self._searcher.query(q).sort(*self.sort_order)


class NeighborhoodsWorker(AreaWorker):
    area_type = 'neighborhood'


class CommunityWorker(AreaWorker):
    area_type = 'community'


class PoliceDistrictWorker(AreaWorker):
    area_type = 'police-district'


class SchoolGroundWorker(AreaWorker):
    area_type = 'school-ground'


class WardWorker(AreaWorker):
    area_type = 'ward'


class BeatWorker(AreaWorker):
    area_type = 'beat'


class UnitOfficerWorker(Worker):
    doc_type_klass = OfficerInfoDocType
    fields = ['unit_name', 'description']
    sort_order = ['-allegation_count']

    def query(self, term, **kwargs):
        return OfficerInfoDocType.search().query('nested', path='historic_units', query=Q(
            'multi_match',
            operator='and',
            fields=['historic_units.{}'.format(field) for field in self.fields],
            query=term
        )).sort(*self.sort_order)


class CrWorker(Worker):
    doc_type_klass = CrDocType
    fields = ['crid', 'incident_date']
    search_with_dates = True

    def query(self, term, **kwargs):
        dates = kwargs.get('dates', [])
        return self._searcher.query(
            'bool',
            should=(
                [Q('term', incident_date=date) for date in dates] +
                [Q('term', crid=term)]
            )
        )


class TRRWorker(Worker):
    doc_type_klass = TRRDocType
    fields = ['_id', 'trr_datetime']
    search_with_dates = True

    def query(self, term, **kwargs):
        dates = kwargs.get('dates', [])
        return self._searcher.query(
            'bool',
            should=(
                [Q('term', trr_datetime=date) for date in dates] +
                [Q('term', _id=term)]
            )
        )
