from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response

from activity_grid.models import ActivityCard
from activity_grid.serializers import OfficerCardSerializer
from officers.workers import OfficerPercentileWorker, OfficerMetricsWorker


class ActivityGridViewSet(viewsets.ViewSet):
    def list(self, request):

        queryset = ActivityCard.objects.all()
        queryset = queryset.annotate(null_position=Count('last_activity'))
        queryset = queryset.order_by('-important', '-null_position', '-last_activity')[:40]

        ids = list(queryset.values_list('officer', flat=True))

        es_results = OfficerPercentileWorker().search(ids, size=40)
        percentile_data = {h.officer_id: h.to_dict() for h in es_results.hits}
        es_results = OfficerMetricsWorker().search(ids, size=40)
        metric_data = {h.id: h.to_dict() for h in es_results.hits}

        results = []
        for obj in queryset:
            officer = obj.officer
            if officer.id in percentile_data:
                officer.percentile = percentile_data[officer.id]
            if officer.id in metric_data:
                officer_metric = metric_data[officer.id]
                officer.sustained_count_metric = officer_metric['sustained_count']
                officer.complaint_count_metric = officer_metric['allegation_count']
            results.append(officer)
        serializer = OfficerCardSerializer(results, many=True)

        return Response(serializer.data)
