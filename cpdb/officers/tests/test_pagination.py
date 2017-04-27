from django.test import SimpleTestCase

from mock import Mock
from robber import expect

from officers.pagination import ESQueryPagination


class ESQueryPaginationTestCase(SimpleTestCase):
    def test_paginate_es_query(self):
        request = Mock()
        request.query_params = {'limit': 20, 'offset': 30}
        search_result = Mock()
        search_result.hits = Mock()
        search_result.hits.total = 50
        search_result.__iter__ = Mock(return_value=iter([1, 2, 3]))
        query = Mock()
        query.__getitem__ = Mock(return_value=query)
        query.execute.return_value = search_result

        pagination = ESQueryPagination()
        paginated_query = pagination.paginate_es_query(query, request)
        query.__getitem__.assert_called_with(slice(30, 50))
        expect(paginated_query).to.eq([1, 2, 3])
        expect(pagination.count).to.eq(50)
        expect(pagination.limit).to.eq(20)
        expect(pagination.offset).to.eq(30)
        expect(pagination.request).to.eq(request)

    def test_pagination_es_query_no_data(self):
        request = Mock()
        request.query_params = {'limit': 20, 'offset': 30}
        search_result = Mock()
        search_result.hits = Mock()
        search_result.hits.total = 0
        search_result.__iter__ = Mock(return_value=iter([]))
        query = Mock()
        query.__getitem__ = Mock(return_value=query)
        query.execute.return_value = search_result

        pagination = ESQueryPagination()
        paginated_query = pagination.paginate_es_query(query, request)

        expect(paginated_query).to.eq([])
