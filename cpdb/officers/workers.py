from search.workers import Worker
from .doc_types import OfficerPercentileDocType, OfficerMetricsDocType


class OfficerPercentileWorker(Worker):
    doc_type_klass = OfficerPercentileDocType

    def _get_lastest_year(self):
        year_max_query = self._searcher.aggs.metric('year_max', 'max', field='year').execute()
        year_max = year_max_query.aggregations.year_max.value
        return year_max if year_max else 0

    def query(self, officer_ids):
        return self._searcher.query(
            'bool',
            must={'term': {'year': self._get_lastest_year()}},
            filter={'terms': {'officer_id': officer_ids}}
        )

    def get_top_officers(self, percentile=99, size=40):
        query = self._searcher.query(
            'bool',
            filter=[
                {'term': {'year': self._get_lastest_year()}},
                {'range': {'percentile_allegation': {'gte': percentile}}}
            ]
        ).sort({'percentile_allegation': 'desc'})
        return self._limit(query, 0, size).execute()


class OfficerMetricsWorker(Worker):
    doc_type_klass = OfficerMetricsDocType

    def query(self, officer_ids):
        return self._searcher.filter('terms', id=officer_ids)
