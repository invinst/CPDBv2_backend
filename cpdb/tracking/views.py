from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import SearchTracking
from .serializers import SearchTrackingSerializer


class SearchTrackingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SearchTrackingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        query_params = self.request.query_params
        sort = query_params['sort'] if 'sort' in query_params else 'asc'
        sort_field = query_params['sort_field'] if 'sort_field' in query_params else 'query'
        sort_param = '{0}{1}'.format('' if sort == 'asc' else '-', sort_field)

        return SearchTracking.objects.order_by(sort_param)
