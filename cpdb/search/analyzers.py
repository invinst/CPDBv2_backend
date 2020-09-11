from elasticsearch_dsl import analyzer, tokenizer, analysis


remove_white_spaces = analysis.char_filter('remove_white_spaces', 'pattern_replace', pattern=' ', replacement='')
remove_new_lines = analysis.char_filter('remove_invalid_chars', 'pattern_replace', pattern='\n', replacement=' ')
remove_apostrophe = analysis.char_filter('remove_apostrophe', 'pattern_replace', pattern='\'', replacement='')

autocomplete = analyzer(
    'autocomplete',
    char_filter=[remove_white_spaces],
    filter=['lowercase'],
    tokenizer=tokenizer(
        'autocomplete', 'ngram', min_gram=2, max_gram=20, token_chars=['letter', 'digit', 'dash_punctuation']
    )
)

autocomplete_search = analyzer(
    'autocomplete_search',
    filter=['lowercase'],
    tokenizer=tokenizer('autocomplete_search', 'pattern', pattern='[^a-zA-Z0-9\-]+')
)

text_analyzer = analyzer(
    'text_analyzer',
    char_filter=[remove_new_lines, remove_apostrophe],
    filter=['lowercase'],
    tokenizer='standard'
)

text_search_analyzer = analyzer(
    'text_search_analyzer',
    char_filter=[remove_apostrophe],
    filter=['lowercase'],
    tokenizer=tokenizer('autocomplete_search', 'pattern', pattern='[^a-zA-Z0-9\-]+')
)
