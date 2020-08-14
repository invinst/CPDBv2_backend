from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import AttachmentFileFactory
from lawsuit.factories import (LawsuitFactory, PaymentFactory)


class LawsuitTestCase(TestCase):
    def setUp(self):
        self.lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            add1='200 ',
            add2='E. Chicago Ave. ',
            city='Chicago IL '
        )

    def test_total_payments(self):
        PaymentFactory(payee='Lucy Bells', settlement='7500', legal_fees=None, lawsuit=self.lawsuit)
        PaymentFactory(payee='Genre Wilson', settlement=None, legal_fees='2500000000', lawsuit=self.lawsuit)
        expect(self.lawsuit.total_payments()).to.eq({
            'total': 2500007500.00,
            'total_settlement': 7500.00,
            'total_legal_fees': 2500000000.00
        })

    def test_str(self):
        expect(f'{self.lawsuit}').to.eq('Lawsuit 00-L-5230')

    def test_lawsuit_has_many_attachment_files(self):
        expect(self.lawsuit.attachment_files.count()).to.eq(0)

        attachment_file_1, attachement_file_2 = AttachmentFileFactory.create_batch(2, owner=self.lawsuit)
        AttachmentFileFactory(owner=LawsuitFactory())
        expect(self.lawsuit.attachment_files.count()).to.eq(2)
        expect(list(self.lawsuit.attachment_files.order_by('id').all())).to.eq([attachment_file_1, attachement_file_2])

    def test_v2_to(self):
        expect(self.lawsuit.v2_to).to.eq('/lawsuit/00-L-5230/')

    def test_address(self):
        expect(self.lawsuit.address).to.eq('200 E. Chicago Ave., Chicago IL')
