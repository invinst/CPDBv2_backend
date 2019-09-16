from django.db.models import Case, When
from rest_framework.pagination import LimitOffsetPagination


class ESBasePagination(LimitOffsetPagination):
    def paginate_es_query(self, query, request, queryset=None, view=None):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        response = query[self.offset: self.offset + self.limit].execute()
        self.count = response.hits.total
        self.request = request
        self.queryset = queryset

        if self.count == 0 or self.offset > self.count:
            return []
        return self.get_response(response)

    def get_response(self, response):
        raise NotImplementedError()


class ESQueryPagination(ESBasePagination):
    def get_response(self, response):
        return list(response)


class ESQuerysetPagination(ESBasePagination):
    def get_response(self, response):
        pk_list = [item.id for item in response]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return self.queryset.filter(id__in=pk_list).order_by(preserved)
