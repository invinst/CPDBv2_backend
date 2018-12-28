from django.contrib.gis.db import models


class OfficerYearlyPercentile(models.Model):
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=False)
    year = models.IntegerField()
    percentile_trr = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    percentile_allegation = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    percentile_allegation_civilian = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    percentile_allegation_internal = models.DecimalField(max_digits=6, decimal_places=4, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['year']),
        ]
