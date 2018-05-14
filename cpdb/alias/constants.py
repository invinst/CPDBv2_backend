from search.search_indexers import ReportIndexer, AreaIndexer, UnitIndexer
from officers.indexers import OfficersIndexer

INDEXER_MAPPINGS = {
    'officer': OfficersIndexer,
    'area': AreaIndexer,
    'report': ReportIndexer,
    'unit': UnitIndexer
}
