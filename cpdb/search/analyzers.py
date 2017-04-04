from elasticsearch_dsl import analyzer, tokenizer
from elasticsearch_dsl.analysis import CustomTokenFilter

stop_filter = CustomTokenFilter('custom_stop', 'stop', stopwords=['unit'])

autocomplete = analyzer(
    'autocomplete',
    filter=['lowercase'],
    tokenizer=tokenizer(
        'autocomplete', 'edge_ngram',
        min_gram=2, max_gram=10, token_chars=['letter', 'digit']))

autocomplete_search = analyzer('autocomplete_search', filter=['lowercase', stop_filter], tokenizer='whitespace')
