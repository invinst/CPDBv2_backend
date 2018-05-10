from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard
from activity_grid.serializers import OfficerCardSerializer
from officers.doc_types import OfficerInfoDocType


class ActivityGridViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ActivityCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset.order_by('-important', '-null_position', '-last_activity')[:40]

        ids = list(queryset.values_list('officer', flat=True))

        results = OfficerInfoDocType.search().query('terms', id=ids)[0:40].execute()
        results = sorted(results, cmp=lambda x, y: ids.index(x.id) - ids.index(y.id))

        serializer = OfficerCardSerializer(results, many=True)
        return Response(serializer.data)
