from django.test import TestCase
from django.db import models

from robber import expect

from data.utils.subqueries import SQCount
from data.factories import OfficerFactory, OfficerAllegationFactory
from data.models import OfficerAllegation


class SQCountTestCase(TestCase):
    def test_count(self):
        officer = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, officer=officer, final_finding='NS')
        OfficerAllegationFactory.create_batch(2, officer=officer, final_finding='SU')

        subquery = OfficerAllegation.objects.filter(officer=models.OuterRef('officer_id'))
        results = list(
            OfficerAllegation.objects.all()
            .annotate(allegation_count=SQCount(subquery.values('id')))
            .annotate(sustained_count=SQCount(subquery.filter(final_finding='SU').values('id')))
            .values('allegation_count', 'sustained_count')
        )

        expect(results).to.have.length(4)
        for obj in results:
            expect(obj['allegation_count']).to.eq(4)
            expect(obj['sustained_count']).to.eq(2)
