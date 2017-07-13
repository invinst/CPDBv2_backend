from search.search_indexers import (
    OfficerIndexer, NeighborhoodsIndexer, FAQIndexer, ReportIndexer, CommunityIndexer, UnitIndexer
)

INDEXER_MAPPINGS = {
    'officer': OfficerIndexer,
    'neighborhood': NeighborhoodsIndexer,
    'community': CommunityIndexer,
    'faq': FAQIndexer,
    'report': ReportIndexer,
    'unit': UnitIndexer
}
