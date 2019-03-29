from django.contrib.gis.db import models
from django.db.models import Q, Count, Prefetch

from data.models import Officer, AttachmentFile, OfficerAllegation, Allegation
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

    @property
    def relevant_documents(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        return AttachmentFile.showing.filter(
            Q(allegation__in=crids) |
            Q(allegation__officerallegation__officer__in=officer_ids) |
            Q(allegation__investigatorallegation__investigator__officer__in=officer_ids) |
            Q(allegation__police_witnesses__in=officer_ids)
        ).distinct().select_related(
            'allegation',
            'allegation__most_common_category',
        ).prefetch_related(
            Prefetch(
                'allegation__officerallegation_set',
                queryset=OfficerAllegation.objects.select_related('officer').all(),
                to_attr='prefetch_officer_allegations'
            )
        ).order_by('allegation__incident_date')

    @property
    def relevant_coaccusals(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        return Officer.objects.filter(
            Q(officerallegation__allegation__officerallegation__officer_id__in=officer_ids) |
            Q(officerallegation__allegation__in=crids)
        ).distinct().exclude(id__in=officer_ids).annotate(coaccusal_count=Count('id')).order_by('-coaccusal_count')

    @property
    def relevant_complaints(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        return Allegation.objects.filter(
            Q(officerallegation__officer__in=officer_ids) |
            Q(investigatorallegation__investigator__officer__in=officer_ids) |
            Q(police_witnesses__in=officer_ids)
        ).exclude(
            crid__in=crids
        ).distinct().select_related(
            'most_common_category',
        ).prefetch_related(
            Prefetch(
                'officerallegation_set',
                queryset=OfficerAllegation.objects.select_related('officer').all(),
                to_attr='prefetch_officer_allegations'
            )
        ).order_by('incident_date')
