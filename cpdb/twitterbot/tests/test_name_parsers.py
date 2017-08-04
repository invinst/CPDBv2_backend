from django.test import SimpleTestCase

from robber import expect
from mock import patch, Mock
from rosette.api import RosetteException

from twitterbot.name_parsers import RosettePersonNameParser


class RosettePersonNameParserTestCase(SimpleTestCase):
    def test_parse(self):
        entities = [
            {'mention': 'Any Name', 'type': 'PERSON'},
            {'mention': 'Any Product', 'type': 'PRODUCT'}
        ]
        mock_api = Mock(return_value=Mock(entities=Mock(return_value={'entities': entities})))
        with patch('twitterbot.name_parsers.API', mock_api):
            parser = RosettePersonNameParser()
            expect(parser.parse('some content')).to.eq(['Any Name'])

    def test_parse_error(self):
        mock_api = Mock(return_value=Mock(entities=Mock(side_effect=RosetteException('', '', ''))))
        with patch('twitterbot.name_parsers.API', mock_api):
            parser = RosettePersonNameParser()
            expect(parser.parse('some content')).to.eq([])
