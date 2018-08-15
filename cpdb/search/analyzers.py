from elasticsearch_dsl import analyzer, tokenizer, analysis
from elasticsearch_dsl.analysis import CustomTokenFilter

stop_filter = CustomTokenFilter('custom_stop', 'stop', stopwords=['unit'])
remove_white_spaces = analysis.char_filter('remove_white_spaces', 'pattern_replace', pattern=' ', replacement='')

autocomplete = analyzer(
    'autocomplete',
    char_filter=[remove_white_spaces],
    filter=['lowercase'],
    tokenizer=tokenizer('autocomplete', 'ngram', min_gram=2, max_gram=20, token_chars=['letter', 'digit'])
)

autocomplete_search = analyzer(
    'autocomplete_search',
    filter=['lowercase', stop_filter],
    tokenizer=tokenizer('autocomplete_search', 'pattern', pattern='[^a-zA-Z0-9]+')
)
