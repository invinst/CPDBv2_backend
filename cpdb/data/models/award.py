from django.contrib.gis.db import models


class Award(models.Model):
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE)
    award_type = models.CharField(max_length=255)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    current_status = models.CharField(max_length=20)
    request_date = models.DateField()
    rank = models.CharField(max_length=100, blank=True)
    last_promotion_date = models.DateField(null=True)
    requester_full_name = models.CharField(max_length=255, null=True)
    ceremony_date = models.DateField(null=True)
    tracking_no = models.CharField(max_length=255, null=True)
