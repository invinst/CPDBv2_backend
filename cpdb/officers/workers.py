from elasticsearch_dsl import Q

from search.workers import Worker
from .doc_types import OfficerPercentileDocType


class PercentileWorker(Worker):
    doc_type_klass = OfficerPercentileDocType

    def query(self, officer_ids):
        combineQ = [Q('term', officer_id=id) for id in officer_ids]
        query = self._searcher.query(Q(
            'bool',
            must=[Q('term', year=2016)],  # TODO: change to aggregate MAX
            should=combineQ
        ))
        return query
