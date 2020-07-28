from django.test.testcases import TestCase

from robber.expect import expect

from lawsuit.factories import (LawsuitFactory, PaymentFactory)


class LawsuitTestCase(TestCase):
    def test_total_payments(self):
        lawsuit = LawsuitFactory()
        PaymentFactory(payee='Lucy Bells', settlement='7500', legal_fees=None, lawsuit=lawsuit)
        PaymentFactory(payee='Genre Wilson', settlement=None, legal_fees='2500000000', lawsuit=lawsuit)
        expect(lawsuit.total_payments()).to.eq({
            'total': 2500007500.00,
            'total_settlement': 7500.00,
            'total_legal_fees': 2500000000.00
        })
