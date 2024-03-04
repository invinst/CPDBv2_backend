from django.test.testcases import TestCase

from robber import expect

from lawsuit.cache_managers import lawsuit_cache_manager
from lawsuit.factories import LawsuitFactory, PaymentFactory


class LawsuitCacheManagerTestCase(TestCase):
    def test_cache_data(self):
        lawsuit_1 = LawsuitFactory()
        PaymentFactory(settlement=7500, legal_fees=0, lawsuit=lawsuit_1)
        PaymentFactory(settlement=0, legal_fees=2500000000, lawsuit=lawsuit_1)
        lawsuit_2 = LawsuitFactory()
        PaymentFactory(settlement=1000, legal_fees=0, lawsuit=lawsuit_2)
        PaymentFactory(settlement=0, legal_fees=200000, lawsuit=lawsuit_2)
        PaymentFactory(settlement=1500, legal_fees=80000, lawsuit=lawsuit_2)

        lawsuit_cache_manager.cache_data()

        lawsuit_1.refresh_from_db()
        lawsuit_2.refresh_from_db()

        expect(lawsuit_1.total_settlement).to.eq(7500)
        expect(lawsuit_1.total_legal_fees).to.eq(2500000000)
        expect(lawsuit_1.total_payments).to.eq(2500007500)
        expect(lawsuit_2.total_settlement).to.eq(2500)
        expect(lawsuit_2.total_legal_fees).to.eq(280000)
        expect(lawsuit_2.total_payments).to.eq(282500)
