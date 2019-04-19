from django.contrib.gis.db import models
from django.db.models import Q

from data.models import Officer
from data.models.common import TimeStampsModel
from pinboard.fields import HexField


class Pinboard(TimeStampsModel):
    id = HexField(hex_length=8, primary_key=True)
    title = models.CharField(max_length=255, default='', blank=True)
    officers = models.ManyToManyField('data.Officer')
    allegations = models.ManyToManyField('data.Allegation')
    trrs = models.ManyToManyField('trr.TRR')
    description = models.TextField(default='', blank=True)

    @property
    def all_officers(self):
        allegation_ids = self.allegations.all().values_list('crid', flat=True)
        trr_ids = self.trrs.all().values_list('id', flat=True)
        return Officer.objects.filter(
            Q(officerallegation__allegation_id__in=allegation_ids) |
            Q(trr__id__in=trr_ids) |
            Q(pinboard__id=self.id)
        ).order_by('first_name', 'last_name').distinct()
