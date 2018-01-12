from es_index.pagination import ESQueryPagination


class SearchQueryPagination(ESQueryPagination):
    default_limit = 30
