from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard
from activity_grid.serializers import ActivityCardSerializer


class ActivityGridViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ActivityCard.objects.all()[:40]
        serializer = ActivityCardSerializer(queryset, many=True)

        return Response(serializer.data)
