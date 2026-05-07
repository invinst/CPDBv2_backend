from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.constants import FINDINGS, FINDINGS_DICT
from .common import TimeStampsModel


class OfficerAllegationFinding(TimeStampsModel):
    officer_allegation = models.ForeignKey(
        'data.OfficerAllegation', on_delete=models.CASCADE)
    allegation_category = models.ForeignKey(
        'data.AllegationCategory', on_delete=models.SET_NULL, to_field='id', null=True)

    recc_finding = models.CharField(
        choices=FINDINGS, max_length=30, blank=True)
    final_finding = models.CharField(
        choices=FINDINGS, max_length=3, blank=True)
    final_outcome_class = models.CharField(max_length=20, blank=True)

    objects = BulkUpdateManager()

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