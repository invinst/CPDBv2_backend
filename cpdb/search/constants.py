from search.search_indexers import (
    UnitIndexer, AreaIndexer, CrIndexer, TRRIndexer,
    RankIndexer, ZipCodeIndexer, SearchTermItemIndexer
)

DEFAULT_INDEXERS = [
    UnitIndexer, AreaIndexer, CrIndexer, TRRIndexer,
    RankIndexer, ZipCodeIndexer, SearchTermItemIndexer
]

DAILY_INDEXERS = [
    UnitIndexer
]
