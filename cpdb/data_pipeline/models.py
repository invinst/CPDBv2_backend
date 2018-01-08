from django.contrib.gis.db import models


class AppliedFixture(models.Model):
    file_name = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
