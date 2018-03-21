from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard
from activity_grid.serializers import ActivityCardSerializer
from officers.workers import PercentileWorker


class ActivityGridViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ActivityCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset.order_by('-important', '-null_position', '-last_activity')[:40]

        ids = list(queryset.values_list('officer', flat=True))

        es_results = PercentileWorker().search(ids, size=40)
        percentile_data = {h.officer_id: h for h in es_results.hits}

        results = []
        for obj in queryset:
            if obj.officer.id in percentile_data:
                obj.officer.percentile = percentile_data[obj.officer.id].to_dict()
            results.append(obj)

        serializer = ActivityCardSerializer(results, many=True)
        return Response(serializer.data)
