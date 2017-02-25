from elasticsearch_dsl import Q

from .doc_types import (
    OfficerDocType, UnitDocType, FAQDocType, ReportDocType, UnitOfficerDocType,
    NeighborhoodsDocType, CommunityDocType, CoAccusedOfficerDocType)


class Worker(object):
    doc_type_klass = None
    fields = []
    name = ''

    @property
    def _searcher(self):
        return self.doc_type_klass().search()

    def _limit(self, search_results, begin, size):
        return search_results[begin:size]

    def query(self, term):
        return self._searcher.query('multi_match', query=term,
                                    operator='and', fields=self.fields)

    def search(self, term, size=10, begin=0):
        return self._limit(self.query(term), begin, size).execute()


class FAQWorker(Worker):
    doc_type_klass = FAQDocType
    fields = ['question', 'answer']


class ReportWorker(Worker):
    doc_type_klass = ReportDocType
    fields = ['excerpt', 'title', 'publication', 'author']


class OfficerWorker(Worker):
    doc_type_klass = OfficerDocType
    fields = ['full_name', 'badge', 'tags']


class UnitWorker(Worker):
    doc_type_klass = UnitDocType
    fields = ['name']


class NeighborhoodsWorker(Worker):
    doc_type_klass = NeighborhoodsDocType
    fields = ['name']


class CommunityWorker(Worker):
    doc_type_klass = CommunityDocType
    fields = ['name']


class CoAccusedOfficerWorker(Worker):
    doc_type_klass = CoAccusedOfficerDocType
    fields = ['co_accused_officer.full_name', 'co_accused_officer.badge']

    def query(self, term):
        return self._searcher.query(
            'nested',
            path='co_accused_officer',
            query=Q('multi_match', query=term, operator='and', fields=self.fields)
        )


class UnitOfficerWorker(Worker):
    doc_type_klass = UnitOfficerDocType
    fields = ['unit_name']

    def query(self, term):
        return super(UnitOfficerWorker, self).query(term).sort('-allegation_count')
