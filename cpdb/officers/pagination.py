from rest_framework.pagination import LimitOffsetPagination


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
