from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericRelation
from django_bulk_update.manager import BulkUpdateManager

from data.models.common import TimeStampsModel
from data.models.attachment_file import AttachmentFile


class Lawsuit(TimeStampsModel):
    case_no = models.CharField(max_length=20, db_index=True, unique=True)
    incident_date = models.DateTimeField(null=True)
    primary_cause = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    add1 = models.CharField(max_length=16, blank=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    point = models.PointField(srid=4326, null=True)
    officers = models.ManyToManyField('data.Officer', related_name='lawsuits')
    attachment_files = GenericRelation(
        AttachmentFile,
        content_type_field='owner_type',
        object_id_field='owner_id',
        related_query_name='lawsuit'
    )

    interactions = ArrayField(models.CharField(max_length=255), default=list)
    services = ArrayField(models.CharField(max_length=255), default=list)
    misconducts = ArrayField(models.CharField(max_length=255), default=list)
    violences = ArrayField(models.CharField(max_length=255), default=list)
    outcomes = ArrayField(models.CharField(max_length=255), default=list)
    airtable_id = models.CharField(max_length=20, db_index=True, unique=True, null=True)
    airtable_updated_at = models.CharField(max_length=30, null=True, blank=True)

    # CACHED COLUMNS

    total_settlement = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    total_legal_fees = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    total_payments = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)


    objects = models.Manager()
    bulk_objects = BulkUpdateManager()

    def __str__(self):
        return f'Lawsuit {self.case_no}'

    @property
    def v2_to(self):
        return f'/lawsuit/{self.case_no}/'

    @property
    def address(self):
        add1 = self.add1.strip()
        add2 = self.add2.strip()
        city = self.city.strip()
        return ', '.join(filter(None, [' '.join(filter(None, [add1, add2])), city]))

    @property
    def attachment(self):
        attachments = self.attachment_files.all()
        return attachments[0] if attachments else None
