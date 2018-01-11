from django.test import TestCase
import itertools
from robber import expect
from mock import Mock, patch

from data.factories import OfficerFactory
from twitterbot.officer_extractor_pipelines import UrlPipeline, TextPipeline


class TextPipelineTestCase(TestCase):
    @patch('twitterbot.text_extractors.TweetTextExtractor.extract')
    @patch('twitterbot.text_extractors.HashTagTextExtractor.extract')
    @patch('twitterbot.text_extractors.URLContentTextExtractor.extract')
    @patch('twitterbot.name_parsers.GoogleNaturalLanguageNameParser.parse')
    @patch('twitterbot.officer_extractors.ElasticSearchOfficerExtractor.get_officers')
    def test_extract_calls_correct_services(
        self, get_officers, parse, url_extract, hash_extract, text_extract
    ):
        tweet1 = Mock(name='1')
        tweet2 = Mock(name='2')
        OfficerFactory(first_name='Ja', last_name='Vert')
        matching_officer = OfficerFactory(first_name='Don', last_name='Juan')

        text_extract.name = 'text'
        hash_extract.name = 'hash'
        url_extract.name = 'url'
        text_extract.return_value = [('some-source', 'foo Don Juan bar')]
        hash_extract.return_value = []
        url_extract.return_value = []
        parse.return_value = [('some-source', 'Don Juan')]
        get_officers.return_value = [('some-source', matching_officer)]

        officers = TextPipeline.extract([tweet1, tweet2])

        for tweet, extract_func in itertools.product([tweet1, tweet2], (text_extract, hash_extract, url_extract)):
            expect(extract_func).to.be.ever_called_with(tweet)
        expect(parse).to.be.called_with(('some-source', 'foo Don Juan bar'))
        expect(get_officers).to.be.called_with([('some-source', 'Don Juan')])

        expect(officers).to.eq([('some-source', matching_officer)])


class UrlPipelineTestCase(TestCase):
    def test_extract_matching_id(self):
        officer = OfficerFactory(id=1234)
        tweets = [
            Mock(urls=[
                'http://some-external-site.com/officer/2345/'
            ]),
            Mock(urls=[
                'http://foo.com/officer/1234/',
                'http://foo.com/complaints/54321/',
                'http://some-external-site.com/officer/2345/'
            ])
        ]
        expect(UrlPipeline.extract(tweets)).to.eq([('cpdb-url', officer)])

    def test_extract_no_matching_id(self):
        OfficerFactory(id=1234)
        tweets = [Mock(urls=[
            'http://foo.com/officer/4567/'
        ])]
        expect(UrlPipeline.extract(tweets)).to.eq([])
