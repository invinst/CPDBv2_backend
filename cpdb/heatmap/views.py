from django.db.models import Count

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from data.models import OfficerAllegation
from data.constants import DISCIPLINE_CODES


class CitySummaryViewSet(ViewSet):
    def list(self, request):
        city_summary = {
            'allegation_count': OfficerAllegation.objects.count(),
            'discipline_count': OfficerAllegation.objects.filter(final_outcome__in=DISCIPLINE_CODES).distinct().count(),
            'most_common_complaints': list(
                OfficerAllegation.objects.values(
                    'allegation_category__category'
                ).annotate(
                    complaints_count=Count('id')
                ).order_by('-complaints_count')[:3].values_list('allegation_category__category', flat=True)
            )
        }

        return Response(city_summary)
