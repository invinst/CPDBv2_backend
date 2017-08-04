from django.test import SimpleTestCase

from robber import expect
from mock import Mock, patch
from requests.exceptions import ConnectionError

from twitterbot.utils import web_parsing


class WebParsingTestCase(SimpleTestCase):
    def test_parse_successfully(self):
        text_content = """
        <html>
        <head>
        </head>
        <body>
        <p>some text</p>
        </body>
        </html>
        """
        mock_response = Mock(content=Mock(decode=Mock(return_value=text_content)))
        with patch('requests.get', return_value=mock_response):
            expect(web_parsing.parse('http://foo.com')).to.eq('some text')

    def test_parse_with_connection_error(self):
        url = 'http://foo.com'
        with patch('requests.get', side_effect=ConnectionError()):
            with patch('twitterbot.utils.web_parsing.logger.error') as mock_error:
                expect(web_parsing.parse(url)).to.eq('')
                mock_error.assert_called_with('ConnectionError while parsing %s' % url)

    def test_parse_with_unicode_error(self):
        url = 'http://foo.com'
        mock_response = Mock(content=Mock(decode=Mock(side_effect=[UnicodeError, ''])))
        with patch('requests.get', return_value=mock_response):
            with patch('twitterbot.utils.web_parsing.logger.error') as mock_error:
                web_parsing.parse(url)
                mock_response.content.decode.assert_called_with('utf-8', 'replace')
                mock_error.assert_called_with('UnicodeError while parsing %s' % url)

    def test_ignore_unnecessary_tags(self):
        text_content = """
        <html>
        <style>some style</style>
        <body>
        <p>some text</p>
        </body>
        </html>
        """
        mock_response = Mock(content=Mock(decode=Mock(return_value=text_content)))
        with patch('requests.get', return_value=mock_response):
            expect(web_parsing.parse('http://foo.com')).to.eq('some text')
