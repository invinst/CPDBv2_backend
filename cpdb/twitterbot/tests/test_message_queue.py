from django.test import SimpleTestCase, override_settings

from mock import patch, Mock

from twitterbot.message_queue import send_tweet


class MessageQueueTestCase(SimpleTestCase):
    @override_settings(AZURE_QUEUE_NAME='queue_bot')
    @patch('twitterbot.message_queue.base64.b64encode', return_value='encoded_text')
    @patch('twitterbot.message_queue.json.dumps')
    @patch('twitterbot.message_queue.QueueService')
    def test_send_tweet(self, QueueService, dumps, _):
        put_mock = Mock()
        QueueService.return_value = Mock(put_message=put_mock)
        entity = {
            'id': 123,
            'percentiles': []
        }
        send_tweet('message', in_reply_to=1, entity=entity)
        dumps.assert_called_with({
            'id': 123,
            'tweet': {
                'status': 'message',
                'in_reply_to_status_id': 1
            },
            'percentiles': []
        })
        put_mock.assert_called_with('queue_bot', u'encoded_text')
