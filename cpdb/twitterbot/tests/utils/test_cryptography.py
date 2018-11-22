import hashlib

from django.test import SimpleTestCase

from robber import expect
from mock import Mock, patch

from twitterbot.utils.cryptography import get_hash_token


class CryptographyTestCase(SimpleTestCase):

    @patch('twitterbot.utils.cryptography.hmac')
    @patch('twitterbot.utils.cryptography.base64')
    def test_get_hash_token(self, base64, hmac):
        hmac.new.return_value = Mock(
            digest=Mock(
                return_value='hash_abc'
            )
        )
        base64.b64encode.return_value = bytes('encoded_hash_abc', 'utf-8')

        token = get_hash_token('key', msg='abc')

        hmac.new.assert_called_with('key', msg='abc', digestmod=hashlib.sha256)
        base64.b64encode.assert_called_with('hash_abc')
        expect(token).to.eq('sha256=encoded_hash_abc')
