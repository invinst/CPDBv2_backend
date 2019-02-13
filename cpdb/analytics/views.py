from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import EventSerializer, SearchTrackingSerializer
from .models import Event, SearchTracking
from .filters import SearchTrackingFilterSet


class EventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)


class SearchTrackingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SearchTrackingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = SearchTracking.objects.all()
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter)
    ordering = ('-query',)
    search_fields = ('query',)
    filter_class = SearchTrackingFilterSet
