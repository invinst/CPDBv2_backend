from django.db.models import Sum

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from data.models import OfficerAllegation
from lawsuit.models import Lawsuit
from data.constants import ALLEGATION_MIN_DATETIME, HEATMAP_END_YEAR
from django.utils.timezone import now


class CitySummaryViewSet(ViewSet):
    def list(self, request):
        officer_allegations = OfficerAllegation.objects.filter(allegation__incident_date__gte=ALLEGATION_MIN_DATETIME)
        total_lawsuit_settlements = Lawsuit.objects.aggregate(
            total_lawsuit_settlements=Sum('total_payments')
        )['total_lawsuit_settlements']

        city_summary = {
            'start_year': ALLEGATION_MIN_DATETIME.year,
            'end_year': HEATMAP_END_YEAR,
            'allegation_count': officer_allegations.count(),
            'discipline_count': officer_allegations.filter(disciplined=True).distinct().count(),
            'lawsuits_count': Lawsuit.objects.count(),
            'total_lawsuit_settlements': '%.2f' % total_lawsuit_settlements if total_lawsuit_settlements else None
        }

        return Response(city_summary)
