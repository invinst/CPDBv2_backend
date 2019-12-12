from django.db.models.functions import TruncDate
from django.db.models import Q

from data.models import Allegation
from trr.models import TRR


class GeographyCrsDataQuery(object):
    def __init__(self, crids, officers):
        self.crids = crids
        self.officer_ids = [officer.id for officer in officers]

    def data(self):
        return Allegation.objects.filter(
            Q(officerallegation__officer_id__in=self.officer_ids) | Q(crid__in=self.crids),
            incident_date__isnull=False,
        ).distinct().select_related(
            'most_common_category'
        ).order_by('crid')


class GeographyTrrsDataQuery(object):
    def __init__(self, trr_ids, officers):
        self.trr_ids = trr_ids
        self.officer_ids = [officer.id for officer in officers]

    def data(self):
        return TRR.objects.filter(
            Q(officer_id__in=self.officer_ids) | Q(id__in=self.trr_ids)
        ).annotate(
            trr_date=TruncDate('trr_datetime')
        ).order_by('id')
