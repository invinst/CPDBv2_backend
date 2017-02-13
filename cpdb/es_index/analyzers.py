from elasticsearch_dsl import analyzer, tokenizer


autocomplete_analyzer = analyzer(
    'autocomplete',
    filter=['lowercase'],
    tokenizer=tokenizer(
        'autocomplete', 'edge_ngram',
        min_gram=2, max_gram=10, token_chars=['letter', 'digit']))

autocomplete_search_analyzer = analyzer('autocomplete_search', filter=['lowercase'], tokenizer='whitespace')
