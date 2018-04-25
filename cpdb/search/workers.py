from elasticsearch_dsl.query import Q

from search.doc_types import CrDocType
from .doc_types import (
    OfficerDocType, UnitDocType, FAQDocType, ReportDocType, UnitOfficerDocType, AreaDocType
)


class Worker(object):
    doc_type_klass = None
    fields = []
    sort_order = []
    name = ''

    @property
    def _searcher(self):
        return self.doc_type_klass().search()

    def _limit(self, search_results, begin, size):
        return search_results[begin:size]

    def query(self, term):
        return self._searcher \
            .query('multi_match', query=term, operator='and', fields=self.fields) \
            .sort(*self.sort_order)

    def search(self, term, size=10, begin=0):
        return self._limit(self.query(term), begin, size).execute()

    def get_sample(self):
        query = self._searcher.query(
            'function_score',
            random_score={}
        ).query(
            'exists',
            field='tags'
        )
        return self._limit(query, 0, 1).execute()


class FAQWorker(Worker):
    doc_type_klass = FAQDocType
    fields = ['question', 'answer', 'tags']


class ReportWorker(Worker):
    doc_type_klass = ReportDocType
    fields = ['excerpt', 'title', 'publication', 'author', 'tags']


class OfficerWorker(Worker):
    doc_type_klass = OfficerDocType

    def query(self, term):
        _query = self._searcher.query(
            'function_score',
            query={
                'multi_match': {
                    'query': term,
                    'fields': ['badge', 'full_name', 'tags', '_id']
                }
            },
            functions=[
                {
                    'filter': {'match': {'tags': term}},
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
                    'filter': {'match': {'full_name': term}},
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
    sort_order = ['name.keyword', '_score']

    def query(self, term):
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
    doc_type_klass = UnitOfficerDocType
    fields = ['unit_name', 'unit_description']
    sort_order = ['-allegation_count']

    def query(self, term):
        return super(UnitOfficerWorker, self).query(term).sort('-allegation_count')


class CrWorker(Worker):
    doc_type_klass = CrDocType
    fields = ['crid']
