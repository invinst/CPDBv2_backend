from django.test import SimpleTestCase, TestCase

from mock import Mock
from robber import expect

from data.factories import AttachmentFileFactory, AllegationFactory
from data.models import AttachmentFile
from es_index.pagination import ESBasePagination, ESQueryPagination, ESQuerysetPagination


class ESBasePaginationTestCase(SimpleTestCase):
    def test_get_response_raise_NotImplementedError(self):
        response = Mock()
        pagination = ESBasePagination()
        expect(lambda: pagination.get_response(response)).to.throw(NotImplementedError)


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


class ESQuerysetPaginationTestCase(TestCase):
    def test_paginate_es_query(self):
        allegation = AllegationFactory(crid=123456)
        attachment_1 = AttachmentFileFactory(
            id=1,
            owner=allegation,
            title='Document Title 1',
            text_content='Text Content 1'
        )
        attachment_2 = AttachmentFileFactory(
            id=2,
            owner=allegation,
            title='Document Title 2',
            text_content='Text Content 2'
        )

        AttachmentFileFactory(
            id=3,
            owner=allegation,
            title='Document Title 3',
            text_content='Text Content 3'
        )
        queryset = AttachmentFile.objects.all()

        class MockObject(object):
            pass

        returned_value_1 = MockObject()
        returned_value_2 = MockObject()
        setattr(returned_value_1, 'id', 1)
        setattr(returned_value_2, 'id', 2)

        request = Mock()
        request.query_params = {'limit': 20, 'offset': 30}
        search_result = Mock()
        search_result.hits = Mock()
        search_result.hits.total = 50
        search_result.__iter__ = Mock(return_value=iter([returned_value_1, returned_value_2]))
        query = Mock()
        query.__getitem__ = Mock(return_value=query)
        query.execute.return_value = search_result

        pagination = ESQuerysetPagination()
        paginated_query = pagination.paginate_es_query(query, request, queryset)
        expect(list(paginated_query)).to.eq([attachment_1, attachment_2])
        expect(pagination.count).to.eq(50)
        expect(pagination.limit).to.eq(20)
        expect(pagination.offset).to.eq(30)
        expect(pagination.request).to.eq(request)

    def test_paginate_es_query_no_data(self):
        allegation = AllegationFactory(crid=123456)
        AttachmentFileFactory(
            id=1,
            owner=allegation,
            title='Document Title 1',
            text_content='Text Content 1'
        )
        AttachmentFileFactory(
            id=2,
            owner=allegation,
            title='Document Title 2',
            text_content='Text Content 2'
        )

        AttachmentFileFactory(
            id=3,
            owner=allegation,
            title='Document Title 3',
            text_content='Text Content 3'
        )
        queryset = AttachmentFile.objects.all()

        class MockObject(object):
            pass

        returned_value_1 = MockObject()
        returned_value_2 = MockObject()
        setattr(returned_value_1, 'id', 4)
        setattr(returned_value_2, 'id', 5)

        request = Mock()
        request.query_params = {'limit': 20, 'offset': 30}
        search_result = Mock()
        search_result.hits = Mock()
        search_result.hits.total = 50
        search_result.__iter__ = Mock(return_value=iter([returned_value_1, returned_value_2]))
        query = Mock()
        query.__getitem__ = Mock(return_value=query)
        query.execute.return_value = search_result

        pagination = ESQuerysetPagination()
        paginated_query = pagination.paginate_es_query(query, request, queryset)
        expect(list(paginated_query)).to.eq([])
