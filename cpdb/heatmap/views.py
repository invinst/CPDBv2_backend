from django.db.models import Count

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from data.models import OfficerAllegation
from data.constants import ALLEGATION_MIN_DATETIME


class CitySummaryViewSet(ViewSet):
    def list(self, request):
        officer_allegations = OfficerAllegation.objects.filter(allegation__incident_date__gte=ALLEGATION_MIN_DATETIME)

        city_summary = {
            'allegation_count': officer_allegations.count(),
            'discipline_count': officer_allegations.filter(disciplined=True).distinct().count(),
            'most_common_complaints': [
                {
                    'name': obj['allegation_category__category'],
                    'count': obj['complaints_count']
                }
                for obj in officer_allegations.values(
                    'allegation_category__category'
                ).annotate(
                    complaints_count=Count('id')
                ).order_by('-complaints_count')[:3].values('allegation_category__category', 'complaints_count')
            ]
        }

        return Response(city_summary)
