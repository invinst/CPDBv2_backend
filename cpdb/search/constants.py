from search.indexers import (
        OfficerIndexer, UnitIndexer, NeighborhoodsIndexer,
        CoAccusedOfficerIndexer, UnitOfficerIndexer,
        CommunityIndexer, FAQIndexer, ReportIndexer)


DEFAULT_INDEXERS = [
    OfficerIndexer, UnitIndexer, NeighborhoodsIndexer,
    CoAccusedOfficerIndexer, CommunityIndexer, FAQIndexer, ReportIndexer,
    UnitOfficerIndexer
]
