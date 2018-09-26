from datetime import date

from django.test import TestCase

from robber import expect

from officers.indexers import AwardNewTimelineEventIndexer
from data.factories import AwardFactory, OfficerFactory, OfficerHistoryFactory, SalaryFactory


class AwardNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AwardFactory(award_type='Honorable Mention')
        AwardFactory(award_type='Honorable Mention Ribbon Award')
        AwardFactory(award_type="Superintendent'S Honorable Mention")
        AwardFactory(award_type='Special Honorable Mention')
        AwardFactory(award_type='Complimentary Letter')
        AwardFactory(award_type='Department Commendation')
        award1 = AwardFactory(award_type='Life Saving Award')
        award2 = AwardFactory(award_type='Award Of Appreciation')
        award3 = AwardFactory(award_type='Problem Solving Award')
        expect(set([
            obj.pk for obj in AwardNewTimelineEventIndexer().get_queryset()
        ])).to.eq(set([award1.id, award2.id, award3.id]))

    def test_extract_datum(self):
        officer = OfficerFactory(id=123)
        AwardFactory(
            officer=officer,
            start_date=date(2010, 3, 4),
            award_type='Abc')
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2009, 1, 1),
            end_date=date(2012, 1, 1),
            unit__unit_name='001',
            unit__description='District 1')
        SalaryFactory(
            officer=officer,
            rank='Police Officer',
            spp_date=date(2009, 1, 1)
        )
        indexer = AwardNewTimelineEventIndexer()
        rows = [indexer.extract_datum(obj) for obj in indexer.get_queryset()]
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 40,
            'date': '2010-03-04',
            'kind': 'AWARD',
            'award_type': 'Abc',
            'unit_name': '001',
            'unit_description': 'District 1',
            'rank': 'Police Officer',
        })
