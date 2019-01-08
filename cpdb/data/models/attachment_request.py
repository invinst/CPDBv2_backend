from django.apps import apps
from django.contrib.gis.db import models
from django.db.models import Exists, OuterRef
from django_bulk_update.manager import BulkUpdateManager

from .common import TimeStampsModel


class AttachmentRequestManager(models.Manager):
    def annotate_investigated_by_cpd(self):
        Allegation = apps.get_app_config('data').get_model('Allegation')
        return self.annotate(has_badge_number=Exists(Allegation.objects.filter(
            crid=OuterRef('allegation_id'),
            investigatorallegation__investigator__officer__officerbadgenumber__isnull=False
        ))).annotate(has_current_star=Exists(Allegation.objects.filter(
            crid=OuterRef('allegation_id'),
            investigatorallegation__current_star__isnull=False
        ))).annotate(investigated_by_cpd=models.Case(
            models.When(allegation__incident_date__year__lt=2006, then=True),
            models.When(has_current_star=True, then=True),
            models.When(has_badge_number=True, then=True),
            default=False,
            output_field=models.BooleanField()
        ))


class AttachmentRequest(TimeStampsModel):
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    status = models.BooleanField(default=False)
    airtable_id = models.CharField(max_length=255, blank=True, default='')

    bulk_objects = BulkUpdateManager()

    objects = AttachmentRequestManager()

    class Meta:
        unique_together = (('allegation', 'email'),)

    def __str__(self):
        return f'{self.email} - {self.allegation.crid}'

    @property
    def crid(self):
        return self.allegation.crid

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AttachmentRequest, self).save(*args, **kwargs)

    def investigator_names(self):
        investigatorallegation_set = self.allegation.investigatorallegation_set.select_related('investigator')
        investigators = [ia.investigator.full_name for ia in investigatorallegation_set.all()]
        return ', '.join(investigators)

    investigator_names.short_description = 'Investigators'
