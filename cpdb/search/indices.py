from es_index.index_aliases import IndexAlias
from .analyzers import autocomplete, autocomplete_search


autocompletes_alias = IndexAlias('autocompletes')
autocompletes = autocompletes_alias.write_index
autocompletes.analyzer(autocomplete)
autocompletes.analyzer(autocomplete_search)
