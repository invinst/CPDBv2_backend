from officers.index_aliases import officers_index_alias
from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer, YearTimelineEventIndexer,
    JoinedTimelineEventIndexer, TimelineMinimapIndexer, SocialGraphIndexer
)


class OfficerSummaryTestCaseMixin(object):
    def setUp(self):
        officers_index_alias._write_index.delete(ignore=404)
        officers_index_alias._read_index.create(ignore=400)

    def refresh_index(self):
        with officers_index_alias.indexing():
            OfficersIndexer().reindex()
            CRTimelineEventIndexer().reindex()
            UnitChangeTimelineEventIndexer().reindex()
            YearTimelineEventIndexer().reindex()
            JoinedTimelineEventIndexer().reindex()
            TimelineMinimapIndexer().reindex()
            SocialGraphIndexer().reindex()
        officers_index_alias._write_index.refresh()
