from django.contrib.gis.db import models


class OfficerAlias(models.Model):
    old_officer_id = models.IntegerField()
    new_officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('old_officer_id', 'new_officer')
