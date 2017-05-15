from es_index import es_client
from officers.indices import officers_index
from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer, YearTimelineEventIndexer,
    JoinedTimelineEventIndexer, TimelineMinimapIndexer
)


class OfficerSummaryTestCaseMixin(object):
    def setUp(self):
        officers_index.delete(ignore=404)
        officers_index.create()

    def refresh_index(self):
        OfficersIndexer().reindex()
        CRTimelineEventIndexer().reindex()
        UnitChangeTimelineEventIndexer().reindex()
        YearTimelineEventIndexer().reindex()
        JoinedTimelineEventIndexer().reindex()
        TimelineMinimapIndexer().reindex()
        es_client.indices.refresh(index='test_officers')
