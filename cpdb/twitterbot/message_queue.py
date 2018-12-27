import json

from django.conf import settings

from azure.storage.queue import QueueService
import base64


def send_tweet(tweet_message, in_reply_to, entity):
    queue_name = settings.AZURE_QUEUE_NAME
    queue_service = QueueService(
        account_name=settings.TWITTERBOT_STORAGE_ACCOUNT_NAME,
        account_key=settings.TWITTERBOT_STORAGE_ACCOUNT_KEY
    )
    queue_service.create_queue(queue_name)

    queue_message = {
        'id': entity['id'],
        'tweet': {
            'status': tweet_message,
            'in_reply_to_status_id': in_reply_to
        },
        'percentiles': entity['percentiles']
    }

    queue_service.put_message(
        queue_name,
        base64.b64encode(json.dumps(queue_message).encode('utf-8')).decode('utf-8')
    )
