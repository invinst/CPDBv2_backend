from search.search_indexers import AreaIndexer, UnitIndexer
from officers.indexers import OfficersIndexer

INDEXER_MAPPINGS = {
    'officer': OfficersIndexer,
    'area': AreaIndexer,
    'unit': UnitIndexer
}
