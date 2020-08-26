from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import AttachmentFileFactory
from lawsuit.factories import LawsuitFactory


class LawsuitTestCase(TestCase):
    def test_total_payments(self):
        lawsuit = LawsuitFactory(total_settlement=2500000, total_legal_fees=None)
        expect(lawsuit.total_payments).to.eq(2500000.00)

        lawsuit = LawsuitFactory(total_settlement=None, total_legal_fees=1200)
        expect(lawsuit.total_payments).to.eq(1200.00)

        lawsuit = LawsuitFactory(total_settlement=2500000, total_legal_fees=1200)
        expect(lawsuit.total_payments).to.eq(2501200.00)

    def test_str(self):
        lawsuit = LawsuitFactory(case_no='00-L-5230')
        expect(f'{lawsuit}').to.eq('Lawsuit 00-L-5230')

    def test_lawsuit_has_many_attachment_files(self):
        lawsuit = LawsuitFactory()
        expect(lawsuit.attachment_files.count()).to.eq(0)

        attachment_file_1, attachement_file_2 = AttachmentFileFactory.create_batch(2, owner=lawsuit)
        AttachmentFileFactory(owner=LawsuitFactory())
        expect(lawsuit.attachment_files.count()).to.eq(2)
        expect(list(lawsuit.attachment_files.order_by('id').all())).to.eq([attachment_file_1, attachement_file_2])

    def test_v2_to(self):
        lawsuit = LawsuitFactory(case_no='00-L-5230')
        expect(lawsuit.v2_to).to.eq('/lawsuit/00-L-5230/')

    def test_address(self):
        lawsuit = LawsuitFactory(
            add1='200 ',
            add2='E. Chicago Ave. ',
            city='Chicago IL '
        )

        expect(lawsuit.address).to.eq('200 E. Chicago Ave., Chicago IL')
