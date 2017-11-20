from elasticsearch_dsl import Q

from .doc_types import (
    OfficerDocType, UnitDocType, FAQDocType, ReportDocType, UnitOfficerDocType,
    NeighborhoodsDocType, CommunityDocType, CoAccusedOfficerDocType)


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
        return self._searcher\
            .query('multi_match', query=term, operator='and', fields=self.fields)\
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
    fields = ['full_name', 'badge', 'tags^10000', '_id']

    def query(self, term):
        _query = self._searcher\
            .query(
                'function_score',
                query={
                    "multi_match": {
                        "query": term,
                        "fields": self.fields
                    }
                },
                script_score={
                    "script": {
                        "lang": "painless",
                        "inline": "_score + doc['allegation_count'].value"
                    }
                }
            )
        return _query


class UnitWorker(Worker):
    doc_type_klass = UnitDocType
    fields = ['name', 'description', 'tags']


class NeighborhoodsWorker(Worker):
    doc_type_klass = NeighborhoodsDocType
    fields = ['name', 'tags']


class CommunityWorker(Worker):
    doc_type_klass = CommunityDocType
    fields = ['name', 'tags']


class CoAccusedOfficerWorker(Worker):
    doc_type_klass = CoAccusedOfficerDocType
    fields = ['co_accused_officer.full_name', 'co_accused_officer.badge', 'co_accused_officer.tags']

    def query(self, term):
        return self._searcher.query(
            'nested',
            path='co_accused_officer',
            query=Q('multi_match', query=term, operator='and', fields=self.fields)
        )


class UnitOfficerWorker(Worker):
    doc_type_klass = UnitOfficerDocType
    fields = ['unit_name']
    sort_order = ['-allegation_count']

    def query(self, term):
        return super(UnitOfficerWorker, self).query(term).sort('-allegation_count')
