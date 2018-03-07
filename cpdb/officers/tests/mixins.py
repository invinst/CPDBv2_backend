from io import StringIO

from mock import mock_open, patch

from officers.index_aliases import officers_index_alias
from officers.indexers import (
    OfficersIndexer, CRTimelineEventIndexer, UnitChangeTimelineEventIndexer,
    JoinedTimelineEventIndexer, SocialGraphIndexer, OfficerPercentileIndexer
)


class OfficerSummaryTestCaseMixin(object):
    def setUp(self):
        officers_index_alias.write_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with officers_index_alias.indexing():
            OfficersIndexer().reindex()
            CRTimelineEventIndexer().reindex()
            UnitChangeTimelineEventIndexer().reindex()
            JoinedTimelineEventIndexer().reindex()
            SocialGraphIndexer().reindex()

            percentile_csv = u'UID,TRR_date,ALL_TRR,CIVILLIAN,INTERNAL,OTHERS,SHOOTING,TASER\n' + \
                             '1.0,2015,0.0,0.67,0.0002,0.0,0.0,0.0010\n' + \
                             '1.0,2016,0.0,0.77,0.0002,0.0,0.45,0.0010'
            with patch('__builtin__.open', mock_open(read_data=percentile_csv)) as mock_file:
                mock_file.return_value = StringIO(percentile_csv)
                OfficerPercentileIndexer().reindex()

        officers_index_alias.write_index.refresh()
