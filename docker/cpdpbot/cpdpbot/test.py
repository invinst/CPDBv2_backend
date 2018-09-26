import unittest
import sys
import json
import base64

from mock import patch, Mock
from robber import expect

from .tweet import TweetSender


mock_logger = Mock()


@patch(
    'cpdpbot.tweet.os.environ',
    {
        'AZURE_QUEUE_NAME': 'cpdpbot',
        'TWITTER_CONSUMER_KEY': 'consumer_key',
        'TWITTER_CONSUMER_SECRET': 'consumer_secret',
        'TWITTER_APP_TOKEN_KEY': 'token_key',
        'TWITTER_APP_TOKEN_SECRET': 'token_secret',
        'AZURE_STORAGE_ACCOUNT_NAME': 'account_name',
        'AZURE_STORAGE_ACCOUNT_KEY': 'account_key'
    })
@patch('cpdpbot.tweet.tweepy.OAuthHandler')
@patch('cpdpbot.tweet.tweepy.API')
@patch('cpdpbot.tweet.VideoTweet')
@patch('cpdpbot.tweet.QueueService')
@patch('cpdpbot.tweet.logging.getLogger', return_value=mock_logger)
@patch('cpdpbot.tweet.print')
class CPDPBotTestCase(unittest.TestCase):
    def test_print_exception(self, mock_print, *args):
        TweetSender().print_exception('something bad')
        mock_print.assert_called_with('something bad', file=sys.stderr)

    def test_print_stdout(self, mock_print, *args):
        TweetSender().print_stdout('something bad')
        mock_print.assert_called_with('something bad')

    def test_signal_handler(self, *args):
        sender = TweetSender()
        sender.signal_handler(Mock(), Mock())
        expect(sender.run).to.be.false()

    def test_status_url(self, *args):
        status = Mock()
        status.user.screen_name = "abc"
        status.id = "123"
        expect(TweetSender().status_url(status)).to.eq('https://twitter.com/abc/status/123/')

    def test_generate_mp4_file(self, *args):
        sender = TweetSender()
        expect(sender.generate_mp4_file(dict())).to.be.none()

        with patch('cpdpbot.tweet.write_mp4', return_value=None) as write_mp4:
            data = {'percentiles': []}
            result = sender.generate_mp4_file(data)
            write_mp4.assert_called_with(data, 0.5, 40)
            expect(result).to.be.none()

        with patch('cpdpbot.tweet.write_mp4', return_value='abc.mp4'):
            data = {'percentiles': []}
            result = sender.generate_mp4_file(data)
            write_mp4.assert_called_with(data, 0.5, 40)
            expect(result).to.eq('abc.mp4')

    def prepare_messages(self, sender, messages):
        messages = [
            Mock(content=base64.b64encode(json.dumps(message).encode('utf-8')))
            for message in messages
        ]
        sender.queue_service.get_messages = Mock(return_value=messages)
        return messages

    def test_process_message(self, *args):
        sender = TweetSender()
        messages = self.prepare_messages(sender, [{'tweet': {'status': 'good day'}}])
        sender.generate_mp4_file = Mock(return_value=None)
        sender.process_messages()

        sender.twitter_api.update_status.assert_called_with(status='good day')
        sender.queue_service.delete_message.assert_called_with(
            sender.queue_name, messages[0].id, messages[0].pop_receipt)

    def test_process_message_with_media(self, *args):
        sender = TweetSender()
        messages = self.prepare_messages(sender, [{'tweet': {'status': 'good day'}}])
        sender.generate_mp4_file = Mock(return_value='abc.mp4')

        sender.process_messages()

        sender.vid_tweet.tweet.assert_called_with('abc.mp4', status='good day')
        sender.queue_service.delete_message.assert_called_with(
            sender.queue_name, messages[0].id, messages[0].pop_receipt)

    def test_process_message_error(self, *args):
        sender = TweetSender()
        messages = self.prepare_messages(sender, [{'tweet': {'status': 'good day'}}])
        sender.generate_mp4_file = Mock()
        sender.generate_mp4_file.side_effect = Exception('something wrong')

        sender.process_messages()

        mock_logger.exception.assert_called_with('Cannot send status: {"tweet": {"status": "good day"}}')
        sender.queue_service.put_message.assert_called_with(sender.fail_queue_name, messages[0].content)
        sender.queue_service.delete_message.assert_called_with(
            sender.queue_name, messages[0].id, messages[0].pop_receipt)


if __name__ == '__main__':
    unittest.main()
