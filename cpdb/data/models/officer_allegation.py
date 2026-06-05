from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.constants import FINDINGS_DICT
from .common import TimeStampsModel


class OfficerAllegation(TimeStampsModel):
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE, null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    officer_age = models.IntegerField(null=True)
    recc_outcome = models.CharField(max_length=100, blank=True)
    final_outcome = models.CharField(max_length=100, blank=True)
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
    def findings(self):
        return self.officerallegationfinding_set.all()

    @property
    def sorted_findings(self):
        # TODO: also add a category sort
        # want it to be so it prefers sustained findings, but also more severe categories
        finding_order = {
            'SU': 1,
            'EX': 2,
            'UN': 3,
            'NS': 4,
            'NAF': 5,
            "AC": 6
        }
        return sorted(self.findings, key=lambda x: finding_order.get(x.recc_finding, 100))

    @property
    def representative_finding(self):
        return self.sorted_findings[0] if self.sorted_findings else None

    @property
    def category(self):
        # TODO: remove, †here should always be an allegation category for every finding
        return (self.representative_finding.allegation_category.category
                if self.representative_finding and self.representative_finding.allegation_category
                else None)

    @property
    def subcategory(self):
        return (self.representative_finding.allegation_category.allegation_name
                if self.representative_finding and self.representative_finding.allegation_category
                else None)

    @property
    def complaint_category_aggregation(self):
        query_set = OfficerAllegation.objects.filter(
            officer__officerhistory__unit=self
        ).values(
            'officerallegationfinding__allegation_category__category'
        ).annotate(
            name=models.F('officerallegationfinding__allegation_category__category'),
            count=models.Count('id', distinct=True),
            sustained_count=models.Count(
                models.Case(
                    models.When(officerallegationfinding__final_finding='SU', then='id'),
                    output_field=models.IntegerField(),
                ),
                distinct=True,
            ),
        ).values('name', 'count', 'sustained_count')
        return list(query_set)

    @property
    def coaccused_count(self):
        return self.allegation.coaccused_count

    @property
    def final_finding_display(self):
        if not self.representative_finding:
            return ''

        try:
            return FINDINGS_DICT[self.representative_finding.final_finding]
        except KeyError:
            return 'Unknown'

    @property
    def recc_finding_display(self):
        if not self.representative_finding:
            return ''

        try:
            return FINDINGS_DICT[self.representative_finding.recc_finding]
        except KeyError:
            return 'Unknown'

    @property
    def victims(self):
        return self.allegation.victims.all()

    @property
    def attachments(self):
        return self.allegation.attachment_files.all()
