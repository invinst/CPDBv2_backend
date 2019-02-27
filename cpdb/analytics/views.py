from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from analytics.models import AttachmentTracking
from data.models import AttachmentFile
from .serializers import EventSerializer, SearchTrackingSerializer
from .models import Event, SearchTracking
from .filters import SearchTrackingFilterSet


class EventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)


class SearchTrackingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SearchTrackingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = SearchTracking.objects.all()
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter)
    ordering = ('-query',)
    search_fields = ('query',)
    filter_class = SearchTrackingFilterSet


class AttachmentTrackingViewSet(viewsets.ViewSet):
    def create(self, request):
        data = request.data
        attachment_file = get_object_or_404(AttachmentFile, id=data.get('attachment_id'))
        AttachmentTracking.objects.create(
            attachment_file=attachment_file,
            accessed_from_page=data.get('accessed_from_page'),
            app=data.get('app')
        )
        return Response(status=status.HTTP_200_OK)
