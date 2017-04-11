from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class ESQueryPagination(LimitOffsetPagination):
    def paginate_es_query(self, query, request, view=None):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        response = query[self.offset: self.offset + self.limit].execute()
        self.count = response.hits.total
        self.request = request

        if self.count == 0 or self.offset > self.count:
            return []
        return list(response)


class TimelinePagination(ESQueryPagination):
    def __init__(self, officer_id):
        ESQueryPagination.__init__(self)
        self.officer_id = officer_id

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data,
            'id': self.officer_id,
        })
