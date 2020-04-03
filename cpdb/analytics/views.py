from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from ipware import get_client_ip

from analytics.models import AttachmentTracking
from data.models import AttachmentFile
from .serializers import EventSerializer, SearchTrackingSerializer
from .models import Event, SearchTracking
from .filters import SearchTrackingFilterSet
from analytics.utils.clicky_tracking import clicky_tracking
from analytics.utils.ga_tracking import ga_tracking


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


class TrackingViewSet(viewsets.ViewSet):
    def create(self, request):
        data = request.data
        ga_data = data.get('ga')
        clicky_data = data.get('clicky')
        if not any([ga_data, clicky_data]):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ip_address, _ = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_data = {'ip_address': ip_address, 'user_agent': user_agent}
        if ga_data:
            ga_tracking({**ga_data, **user_data})
        if clicky_data:
            clicky_tracking({**clicky_data, **user_data})
        return Response(status=status.HTTP_200_OK)
