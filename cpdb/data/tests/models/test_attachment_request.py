from django.test.testcases import TestCase
from django.core.validators import ValidationError
from robber.expect import expect

from data.factories import AttachmentRequestFactory, AllegationFactory
from data.models import AttachmentRequest


class AttachmentRequestTestCase(TestCase):
    def test_default_status(self):
        attachment_request = AttachmentRequestFactory()
        expect(attachment_request.status).to.be.false()

    def test_str(self):
        attachment_request = AttachmentRequestFactory.build(
            allegation=AllegationFactory(crid='1111'),
            email='foo@bar.com'
        )
        expect(str(attachment_request)).to.eq('foo@bar.com - 1111')

    def test_crid(self):
        attachment_request = AttachmentRequestFactory.build(
            allegation=AllegationFactory(crid='1111'),
        )
        expect(attachment_request.crid).to.eq('1111')

    def test_email_validation(self):
        expect(lambda: AttachmentRequestFactory(email='foo')).to.throw(ValidationError)

    def test_unique_allegation_and_email(self):
        allegation = AllegationFactory()
        email = 'foo@bar.com'
        AttachmentRequestFactory(email=email, allegation=allegation)

        expect(lambda: AttachmentRequestFactory(email=email, allegation=allegation)).to.throw(ValidationError)
        expect(len(AttachmentRequest.objects.all())).to.eq(1)
