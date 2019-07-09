from django.db.models.functions import TruncDate

from data.models import Allegation
from social_graph.serializers.cr_serializer import CRSerializer
from social_graph.serializers.trr_serializer import TRRSerializer
from social_graph.serializers.cr_preview_pane_serializer import CRPreviewPaneSerializer
from social_graph.serializers.trr_preview_pane_serializer import TRRPreviewPaneSerializer
from trr.models import TRR


class GeographyDataQuery(object):
    def __init__(self, officers, detail=False):
        self.officer_ids = [officer.id for officer in officers]
        self.detail = detail

    @property
    def _cr_data(self):
        cr_queryset = Allegation.objects.filter(
            officerallegation__officer_id__in=self.officer_ids,
            incident_date__isnull=False,
        ).distinct().select_related(
            'most_common_category'
        )
        if self.detail:
            cr_queryset = cr_queryset.prefetch_related(
                'officerallegation_set',
                'officerallegation_set__officer',
                'officerallegation_set__allegation_category',
                'victims',
            )

        serializer = CRPreviewPaneSerializer if self.detail else CRSerializer
        return serializer(cr_queryset, many=True).data

    @property
    def _trr_data(self):
        trr_queryset = TRR.objects.filter(
            officer_id__in=self.officer_ids
        ).annotate(
            trr_date=TruncDate('trr_datetime')
        )

        if self.detail:
            trr_queryset = trr_queryset.select_related('officer')

        serializer = TRRPreviewPaneSerializer if self.detail else TRRSerializer
        return serializer(trr_queryset, many=True).data

    def execute(self):
        return self._cr_data + self._trr_data
