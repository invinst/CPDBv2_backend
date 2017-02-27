from es_index import es_client
from report_bottomsheet.indices import report_bottomsheet_index
from report_bottomsheet.indexers import OfficerIndexer


class ReportBottomSheetTestCaseMixin(object):
    def setUp(self):
        report_bottomsheet_index.delete(ignore=404)
        report_bottomsheet_index.create()

    def refresh_index(self):
        OfficerIndexer().reindex()
        es_client.indices.refresh(index="test_report_bottomsheet")
