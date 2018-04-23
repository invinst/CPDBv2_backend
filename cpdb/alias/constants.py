from search.search_indexers import (
    OfficerIndexer, FAQIndexer, ReportIndexer, AreaIndexer, UnitIndexer
)

INDEXER_MAPPINGS = {
    'officer': OfficerIndexer,
    'area': AreaIndexer,
    'faq': FAQIndexer,
    'report': ReportIndexer,
    'unit': UnitIndexer
}
