from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import SearchTracking
from .serializers import SearchTrackingSerializer


class SearchTrackingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SearchTrackingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    queryset = SearchTracking.objects.all()
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-query',)
