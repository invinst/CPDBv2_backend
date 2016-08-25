from django.test.testcases import SimpleTestCase

from mock import patch, Mock

from vftg.mailchimp_service import MailchimpService, MailchimpAPIError


class MailchimpServiceTestCase(SimpleTestCase):
    def test_subscribe_success(self):
        response = Mock()
        response.status_code = 200
        with patch('requests.post', return_value=response):
            MailchimpService.subscribe('john@doe.com')

    def test_subscribe_failure(self):
        response = Mock()
        response.status_code = 400
        response.content = '{"detail": "email is invalid"}'
        with patch('requests.post', return_value=response):
            with self.assertRaises(MailchimpAPIError) as cm:
                MailchimpService.subscribe('john@doe.com')

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.value, 'email is invalid')
