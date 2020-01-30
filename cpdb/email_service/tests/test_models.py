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

        message = template.create_message(
            to=['to@citizen.com'],
            cc=['cc@citizen.com'],
            tag='Test',
            url='http://cr-document.com/',
            crid='123'
        )

        expect(message.subject).to.eq('Test message')
        expect(message.body).to.eq('This body may contain markdown code and tags (e.g. url http://cr-document.com/)\n')
        expect(message.from_email).to.eq('test.email@cpdp.co')
        expect(message.to).to.eq(['to@citizen.com'])
        expect(message.cc).to.eq(['cc@citizen.com'])
