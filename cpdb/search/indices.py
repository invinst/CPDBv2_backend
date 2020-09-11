from es_index.index_aliases import IndexAlias
from .analyzers import autocomplete, autocomplete_search, text_analyzer, text_search_analyzer


autocompletes_alias = IndexAlias('autocompletes')
autocompletes = autocompletes_alias.write_index
autocompletes.analyzer(autocomplete)
autocompletes.analyzer(autocomplete_search)
autocompletes.analyzer(text_analyzer)
autocompletes.analyzer(text_search_analyzer)
