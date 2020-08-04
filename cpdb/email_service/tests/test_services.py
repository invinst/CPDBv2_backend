from smtplib import SMTPException

from django.test import override_settings
from django.test.testcases import TestCase

from mock import patch
from robber import expect

from email_service.factories import EmailTemplateFactory
from email_service.constants import CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE
from email_service.service import send_attachment_request_email, send_cr_attachment_available_email
from data.factories import AllegationFactory, AttachmentRequestFactory, AttachmentFileFactory
from data.models import AttachmentFile, AttachmentRequest


class EmailServicesTestCase(TestCase):
    @patch('email_service.models.EmailMultiAlternatives.send')
    def test_send_attachment_request_email(self, mock_send_email):
        EmailTemplateFactory(
            subject='To {name}',
            body='This body may contain **markdown code** and tags (e.g. url {url})',
            from_email='test.email@cpdp.co',
            type=CR_ATTACHMENT_REQUEST
        )

        send_attachment_request_email(
            email='alex@citizen.com',
            attachment_type=CR_ATTACHMENT_REQUEST,
            tag='Test',
            url='http://cr-document.com/',
            crid='123'
        )

        mock_send_email.assert_called_once()

    @override_settings(DOCUMENT_REQUEST_CC_EMAIL='cc@email.com', DOMAIN='http://foo.com')
    @patch('email_service.models.EmailMultiAlternatives')
    def test_send_cr_attachment_available_email(self, MockEmailMultiAlternatives):
        EmailTemplateFactory(
            subject='To {name}',
            body='This message is related to crid {pk} with url {url}',
            from_email='test.email@cpdp.co',
            type=CR_ATTACHMENT_AVAILABLE
        )

        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentRequestFactory(
            allegation=allegation_123, email='to.be.notified@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_123, email='notified@citizen.com', noti_email_sent=True)
        AttachmentRequestFactory(
            allegation=allegation_123, email='another.to.be.notified@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_456, email='still.waiting@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_456, email='to.be.notified@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_789, email='to.be.notified@citizen.com', noti_email_sent=False)

        attachment_file_123_a = AttachmentFileFactory(owner=allegation_123)
        attachment_file_123_b = AttachmentFileFactory(owner=allegation_123)
        attachment_file_789 = AttachmentFileFactory(owner=allegation_789)

        send_cr_attachment_available_email([attachment_file_123_a, attachment_file_123_b, attachment_file_789])

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To to.be.notified',
            body='This message is related to crid 123 with url http://foo.com/complaint/123/\n',
            from_email='test.email@cpdp.co',
            to=['to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 123 with url http://foo.com/complaint/123/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To to.be.notified',
            body='This message is related to crid 789 with url http://foo.com/complaint/789/\n',
            from_email='test.email@cpdp.co',
            to=['to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 789 with url http://foo.com/complaint/789/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To another.to.be.notified',
            body='This message is related to crid 123 with url http://foo.com/complaint/123/\n',
            from_email='test.email@cpdp.co',
            to=['another.to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 123 with url http://foo.com/complaint/123/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives().send.call_count).to.be.eq(3)

        expect(
            AttachmentRequest.objects.get(
                allegation=allegation_123,
                email='to.be.notified@citizen.com'
            ).noti_email_sent
        ).to.be.true()
        expect(
            AttachmentRequest.objects.get(
                allegation=allegation_123,
                email='another.to.be.notified@citizen.com'
            ).noti_email_sent
        ).to.be.true()
        expect(
            AttachmentRequest.objects.get(
                allegation=allegation_789,
                email='to.be.notified@citizen.com'
            ).noti_email_sent
        ).to.be.true()
        expect(
            AttachmentRequest.objects.get(
                allegation=allegation_456,
                email='still.waiting@citizen.com'
            ).noti_email_sent
        ).to.be.false()

        attachment_file_123_a.refresh_from_db()
        attachment_file_123_b.refresh_from_db()
        attachment_file_789.refresh_from_db()

        expect(attachment_file_123_a.notifications_count).to.eq(2)
        expect(attachment_file_123_b.notifications_count).to.eq(2)
        expect(attachment_file_789.notifications_count).to.eq(1)

    @override_settings(DOCUMENT_REQUEST_CC_EMAIL='cc@email.com', DOMAIN='http://foo.com')
    @patch('email_service.models.EmailMultiAlternatives')
    def test_send_cr_attachment_available_email_raise_error(self, MockEmailMultiAlternatives):
        MockEmailMultiAlternatives().send.side_effect = [None, SMTPException('Sending failed'), None]

        EmailTemplateFactory(
            subject='To {name}',
            body='This message is related to crid {pk} with url {url}',
            from_email='test.email@cpdp.co',
            type=CR_ATTACHMENT_AVAILABLE
        )

        allegation_123 = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentRequestFactory(
            allegation=allegation_123, email='to.be.notified@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_456, email='to.be.notified@citizen.com', noti_email_sent=False)
        AttachmentRequestFactory(
            allegation=allegation_789, email='to.be.notified@citizen.com', noti_email_sent=False)

        AttachmentFileFactory.create_batch(2, owner=allegation_123)
        AttachmentFileFactory.create_batch(2, owner=allegation_456)
        AttachmentFileFactory(owner=allegation_789)
        new_attachments = AttachmentFile.objects.all()

        send_cr_attachment_available_email(new_attachments)

        expect(AttachmentRequest.objects.filter(noti_email_sent=True).count()).to.eq(2)
        expect(AttachmentRequest.objects.filter(noti_email_sent=False).count()).to.eq(1)

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To to.be.notified',
            body='This message is related to crid 123 with url http://foo.com/complaint/123/\n',
            from_email='test.email@cpdp.co',
            to=['to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 123 with url http://foo.com/complaint/123/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To to.be.notified',
            body='This message is related to crid 456 with url http://foo.com/complaint/456/\n',
            from_email='test.email@cpdp.co',
            to=['to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 456 with url http://foo.com/complaint/456/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives).to.be.any_call(
            subject='To to.be.notified',
            body='This message is related to crid 789 with url http://foo.com/complaint/789/\n',
            from_email='test.email@cpdp.co',
            to=['to.be.notified@citizen.com'],
            cc=['cc@email.com'],
        )
        expect(MockEmailMultiAlternatives().attach_alternative).to.be.any_call(
            '<p>This message is related to crid 789 with url http://foo.com/complaint/789/</p>\n', 'text/html'
        )

        expect(MockEmailMultiAlternatives().send.call_count).to.be.eq(3)

    @patch('email_service.service.logger')
    @patch('email_service.models.EmailMultiAlternatives.send')
    def test_logging_when_sending_cr_attachment_available_email_raise_error(self, mock_send_email, mock_logger):
        mock_send_email.side_effect = SMTPException('Sending failed')

        EmailTemplateFactory(
            subject='To {name}',
            body='This message is related to crid {pk} with url {url}',
            from_email='test.email@cpdp.co',
            type=CR_ATTACHMENT_AVAILABLE
        )

        allegation_123 = AllegationFactory(crid='123')
        AttachmentRequestFactory(allegation=allegation_123, email='to.be.notified@citizen.com', noti_email_sent=False)

        AttachmentFileFactory(owner=allegation_123)
        new_attachments = AttachmentFile.objects.all()

        send_cr_attachment_available_email(new_attachments)

        expect(AttachmentRequest.objects.filter(noti_email_sent=True).count()).to.eq(0)
        expect(AttachmentRequest.objects.filter(noti_email_sent=False).count()).to.eq(1)

        expect(mock_logger.info).to.be.called_with(
            'Cannot send notification email for crid 123 to to.be.notified@citizen.com'
        )
