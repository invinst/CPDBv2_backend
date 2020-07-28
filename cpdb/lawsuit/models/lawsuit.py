from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class Lawsuit(TimeStampsModel):
    case_no = models.CharField(max_length=20, db_index=True, unique=True)
    incident_date = models.DateTimeField(null=True)
    summary = models.TextField()
    location = models.CharField(max_length=64, blank=True)
    add1 = models.CharField(max_length=16, blank=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    officers = models.ManyToManyField('data.Officer')

    interactions = models.ManyToManyField('lawsuit.LawsuitInteraction')
    services = models.ManyToManyField('lawsuit.LawsuitService')
    misconducts = models.ManyToManyField('lawsuit.LawsuitMisconduct')
    violences = models.ManyToManyField('lawsuit.LawsuitViolence')
    outcomes = models.ManyToManyField('lawsuit.LawsuitOutcome')

    def total_payments(self):
        total_settlements = sum(payment.settlement or 0 for payment in self.payments.all())
        total_legal_fees = sum(payment.legal_fees or 0 for payment in self.payments.all())
        return {
            'total': total_settlements + total_legal_fees,
            'total_settlement': total_settlements,
            'total_legal_fees': total_legal_fees
        }
