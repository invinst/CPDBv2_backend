from django.test.testcases import TestCase

from robber import expect

from email_service.factories import EmailTemplateFactory


class EmailTemplateTestCase(TestCase):
    def test_create_message(self):
        template = EmailTemplateFactory(
            subject='{tag} message',
            body='This body may contain **markdown code** and tags (e.g. url {url})',
            from_email='test.email@cpdp.co'
        )

        expect(
            template.create_message(
                recipient_list=['to@citizen.com'],
                tag='Test',
                url='http://cr-document.com/',
                crid='123'
            )
        ).to.eq({
            'subject': 'Test message',
            'message': 'This body may contain markdown code and tags (e.g. url http://cr-document.com/)\n',
            'html_message': '<p>This body may contain <strong>markdown code</strong> and'
                       ' tags (e.g. url http://cr-document.com/)</p>\n',
            'from_email': 'test.email@cpdp.co',
            'recipient_list': ['to@citizen.com']
        })
