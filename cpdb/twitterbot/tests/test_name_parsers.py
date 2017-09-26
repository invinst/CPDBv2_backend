from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from twitterbot.name_parsers import GoogleNaturalLanguageNameParser


class GoogleNaturalLanguageNameParserTestCase(SimpleTestCase):
    def test_parse(self):
        mock_person = Mock(type=1)
        mock_person.name = 'Jason Van Dyke'
        mock_other = Mock(type=7)
        mock_other.name = 'something'

        entities = [mock_person, mock_other]

        mock_client = Mock()
        mock_client.analyze_entities = Mock(return_value=Mock(entities=entities))
        parser = GoogleNaturalLanguageNameParser()
        parser.client = mock_client
        entities = parser.parse(('source', 'Who is Jason Van Dyke something?'))
        expect(entities).to.eq([('source', 'Jason Van Dyke')])
