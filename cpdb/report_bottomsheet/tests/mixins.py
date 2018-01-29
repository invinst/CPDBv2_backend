from report_bottomsheet.index_aliases import report_bottomsheet_index_alias
from report_bottomsheet.indexers import OfficerIndexer


class ReportBottomSheetTestCaseMixin(object):
    def setUp(self):
        report_bottomsheet_index_alias.write_index.delete(ignore=404)
        report_bottomsheet_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with report_bottomsheet_index_alias.indexing():
            OfficerIndexer().reindex()
        report_bottomsheet_index_alias.write_index.refresh()
