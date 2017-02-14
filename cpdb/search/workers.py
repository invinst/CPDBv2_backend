from .doc_types import (
    OfficerDocType, UnitDocType, FAQDocType, ReportDocType,
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

    def search(self, term, size=10, begin=0):
        search_results = self._searcher.query('multi_match', query=term,
                                              operator='and', fields=self.fields)
        return self._limit(search_results, begin, size).execute()


class FAQWorker(Worker):
    doc_type_klass = FAQDocType
    fields = ['question', 'answer']


class ReportWorker(Worker):
    doc_type_klass = ReportDocType
    fields = ['excerpt', 'title', 'publication', 'author']


class OfficerWorker(Worker):
    doc_type_klass = OfficerDocType
    fields = ['full_name', 'badge']


class UnitWorker(Worker):
    doc_type_klass = UnitDocType
    fields = ['name', 'description']


class NeighborhoodsWorker(Worker):
    doc_type_klass = NeighborhoodsDocType
    fields = ['name']


class CommunityWorker(Worker):
    doc_type_klass = CommunityDocType
    fields = ['name']


class CoAccusedOfficerWorker(Worker):
    doc_type_klass = CoAccusedOfficerDocType
    fields = ['full_name', 'badge']

    def search(self, term, size=5, begin=0):
        search_results = self._searcher.query('multi_match', query=term,
                                              operator='and', fields=self.fields)
        return self._limit(search_results, begin, size).execute()
