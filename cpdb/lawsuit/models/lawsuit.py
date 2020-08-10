from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericRelation

from data.models.common import TimeStampsModel
from data.models.attachment_file import AttachmentFile


class Lawsuit(TimeStampsModel):
    case_no = models.CharField(max_length=20, db_index=True, unique=True)
    incident_date = models.DateTimeField(null=True)
    summary = models.TextField()
    location = models.CharField(max_length=64, blank=True)
    add1 = models.CharField(max_length=16, blank=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    point = models.PointField(srid=4326, null=True)
    officers = models.ManyToManyField('data.Officer')
    attachment_files = GenericRelation(
        AttachmentFile,
        content_type_field='owner_type',
        object_id_field='owner_id',
        related_query_name='lawsuit'
    )

    interactions = models.ManyToManyField('lawsuit.LawsuitInteraction')
    services = models.ManyToManyField('lawsuit.LawsuitService')
    misconducts = models.ManyToManyField('lawsuit.LawsuitMisconduct')
    violences = models.ManyToManyField('lawsuit.LawsuitViolence')
    outcomes = models.ManyToManyField('lawsuit.LawsuitOutcome')

    def __str__(self):
        return f'Lawsuit {self.case_no}'

    def total_payments(self):
        total_settlements = sum(payment.settlement or 0 for payment in self.payments.all())
        total_legal_fees = sum(payment.legal_fees or 0 for payment in self.payments.all())
        return {
            'total': total_settlements + total_legal_fees,
            'total_settlement': total_settlements,
            'total_legal_fees': total_legal_fees
        }
