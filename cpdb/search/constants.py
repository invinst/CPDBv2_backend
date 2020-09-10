from search.search_indexers import (
    UnitIndexer, AreaIndexer, CrIndexer, TRRIndexer,
    RankIndexer, ZipCodeIndexer, SearchTermItemIndexer, LawsuitIndexer
)

DEFAULT_INDEXERS = [
    UnitIndexer, AreaIndexer, CrIndexer, TRRIndexer,
    RankIndexer, ZipCodeIndexer, SearchTermItemIndexer, LawsuitIndexer
]

DAILY_INDEXERS = [
    CrIndexer, LawsuitIndexer
]
