from django.db.models.functions import TruncDate

from data.models import Allegation
from trr.models import TRR


class GeographyDataQuery(object):
    def __init__(self, officers):
        self.officer_ids = [officer.id for officer in officers]

    def cr_data(self):
        return Allegation.objects.filter(
            officerallegation__officer_id__in=self.officer_ids,
            incident_date__isnull=False,
        ).distinct().select_related(
            'most_common_category'
        ).order_by('crid')

    def trr_data(self):
        return TRR.objects.filter(
            officer_id__in=self.officer_ids
        ).annotate(
            trr_date=TruncDate('trr_datetime')
        ).order_by('id')
