from django.db.models.functions import TruncDate

from data.models import Allegation
from pinboard.serializers.cr_pinboard_serializer import CRPinboardSerializer
from pinboard.serializers.trr_pinboard_serializer import TRRPinboardSerializer
from trr.models import TRR


class GeographyDataQuery(object):
    def __init__(self, officers):
        self.officer_ids = [officer.id for officer in officers]

    @property
    def _cr_data(self):
        cr_queryset = Allegation.objects.filter(
            officerallegation__officer_id__in=self.officer_ids,
            incident_date__isnull=False,
        ).distinct().select_related(
            'most_common_category'
        ).prefetch_related(
            'victims'
        )

        return CRPinboardSerializer(cr_queryset, many=True).data

    @property
    def _trr_data(self):
        trr_queryset = TRR.objects.filter(
            officer_id__in=self.officer_ids
        ).annotate(
            trr_date=TruncDate('trr_datetime')
        )
        return TRRPinboardSerializer(trr_queryset, many=True).data

    def execute(self):
        return self._cr_data + self._trr_data
