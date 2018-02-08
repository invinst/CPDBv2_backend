from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard
from activity_grid.serializers import ActivityCardSerializer


class ActivityGridViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ActivityCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset.order_by('-important', '-null_position', '-last_activity')[:40]
        serializer = ActivityCardSerializer(queryset, many=True)

        return Response(serializer.data)
