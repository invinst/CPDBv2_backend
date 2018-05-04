from search.search_indexers import (
    NeighborhoodsIndexer, FAQIndexer, ReportIndexer, CommunityIndexer, UnitIndexer
)
from officers.indexers import OfficersIndexer

INDEXER_MAPPINGS = {
    'officer': OfficersIndexer,
    'neighborhood': NeighborhoodsIndexer,
    'community': CommunityIndexer,
    'faq': FAQIndexer,
    'report': ReportIndexer,
    'unit': UnitIndexer
}
