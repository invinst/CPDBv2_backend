from search.workers import Worker
from .doc_types import OfficerPercentileDocType


class PercentileWorker(Worker):
    doc_type_klass = OfficerPercentileDocType

    def query(self, officer_ids):
        year_max_query = self._searcher.aggs.metric('year_max', 'max', field='year').execute()
        year_max = year_max_query.aggregations.year_max.value

        return self._searcher.query(
            'bool',
            must={'term': {'year': year_max if year_max else 0}},
            filter={'terms': {'officer_id': officer_ids}}
        )
