from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from .serializers import EventSerializer
from .models import Event


class EventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (AllowAny,)
