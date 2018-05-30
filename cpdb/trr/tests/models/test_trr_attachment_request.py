from django.test.testcases import TestCase
from django.core.validators import ValidationError
from robber.expect import expect

from trr.factories import TRRAttachmentRequestFactory, TRRFactory
from trr.models import TRRAttachmentRequest


class TRRAttachmentRequestTestCase(TestCase):
    def test_default_status(self):
        attachment_request = TRRAttachmentRequestFactory()
        expect(attachment_request.status).to.be.false()

    def test_str(self):
        attachment_request = TRRAttachmentRequestFactory(
            trr=TRRFactory(pk=1111),
            email='foo@bar.com'
        )
        expect(str(attachment_request)).to.eq('foo@bar.com - 1111')

    def test_email_validation(self):
        expect(lambda: TRRAttachmentRequestFactory(email='foo')).to.throw(ValidationError)

    def test_unique_trr_and_email(self):
        trr = TRRFactory()
        email = 'foo@bar.com'
        TRRAttachmentRequestFactory(email=email, trr=trr)

        expect(lambda: TRRAttachmentRequestFactory(email=email, trr=trr)).to.throw(ValidationError)
        expect(len(TRRAttachmentRequest.objects.all())).to.eq(1)
