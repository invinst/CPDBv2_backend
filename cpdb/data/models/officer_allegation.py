from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.constants import FINDINGS, FINDINGS_DICT
from .common import TimeStampsModel


class OfficerAllegation(TimeStampsModel):
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE, null=True)
    allegation_category = models.ForeignKey(
        'data.AllegationCategory', on_delete=models.SET_NULL, to_field='id', null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    officer_age = models.IntegerField(null=True)

    recc_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    recc_outcome = models.CharField(max_length=32, blank=True)
    final_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    final_outcome = models.CharField(max_length=32, blank=True)
    final_outcome_class = models.CharField(max_length=20, blank=True)
    disciplined = models.NullBooleanField()

    objects = BulkUpdateManager()

    class Meta:
        indexes = [
            models.Index(fields=['start_date']),
        ]

    @property
    def crid(self):
        return self.allegation.crid

    @property
    def category(self):
        try:
            return self.allegation_category.category
        except AttributeError:
            return None

    @property
    def subcategory(self):
        try:
            return self.allegation_category.allegation_name
        except AttributeError:
            return None

    @property
    def coaccused_count(self):
        return self.allegation.coaccused_count

    @property
    def final_finding_display(self):
        try:
            return FINDINGS_DICT[self.final_finding]
        except KeyError:
            return 'Unknown'

    @property
    def recc_finding_display(self):
        try:
            return FINDINGS_DICT[self.recc_finding]
        except KeyError:
            return 'Unknown'

    @property
    def victims(self):
        return self.allegation.victims.all()

    @property
    def attachments(self):
        return self.allegation.attachment_files.all()

    @property
    def filtered_attachments(self):
        return self.allegation.filtered_attachment_files.all()
