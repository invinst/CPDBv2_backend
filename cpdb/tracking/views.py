from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import SearchTracking
from .serializers import SearchTrackingSerializer
from .filters import SearchTrackingFilterSet


class SearchTrackingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SearchTrackingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = SearchTracking.objects.all()
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter)
    ordering = ('-query',)
    search_fields = ('query',)
    filter_class = SearchTrackingFilterSet
