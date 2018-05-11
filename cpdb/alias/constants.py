from search.search_indexers import (
    FAQIndexer, ReportIndexer, AreaIndexer, UnitIndexer
)
from officers.indexers import OfficersIndexer

INDEXER_MAPPINGS = {
    'officer': OfficersIndexer,
    'area': AreaIndexer,
    'faq': FAQIndexer,
    'report': ReportIndexer,
    'unit': UnitIndexer
}
