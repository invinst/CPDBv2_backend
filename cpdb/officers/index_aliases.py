from es_index.index_aliases import IndexAlias
from search.analyzers import autocomplete, autocomplete_search


officers_index_alias = IndexAlias('officers')
# Register analyzers so badge/full_name use n-gram tokenization; required for
# substring matches (e.g. 4-digit badge "7432" matching stored "17432").
officers_index_alias.write_index.analyzer(autocomplete)
officers_index_alias.write_index.analyzer(autocomplete_search)
