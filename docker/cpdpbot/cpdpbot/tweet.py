from __future__ import print_function
import os
import sys
import json
import time
import traceback
import signal
import base64

import tweepy
from azure.storage.queue import QueueService

from .movie import write_mp4
from .video_tweet import VideoTweet


run = True


def print_stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


def print_stdout(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def signal_handler(signal, frame):
    global run
    print_stdout('Exiting...')
    run = False


def status_url(status):
    return 'https://twitter.com/%s/status/%s/' % (status.user.screen_name, status.id)


def generate_mp4_file(data, yd, fps):
    if 'percentiles' in data:
        return write_mp4(data, yd, fps)
    return None


def main():
    signal.signal(signal.SIGINT, signal_handler)
    fps = int(os.environ.get('FPS', '40'))
    yd = float(os.environ.get('YEAR_DURATION', '0.5'))
    queue_name = os.environ['AZURE_QUEUE_NAME']
    fail_queue_name = '%sfail' % queue_name

    twitter_auth = tweepy.OAuthHandler(
        os.environ['TWITTER_CONSUMER_KEY'],
        os.environ['TWITTER_CONSUMER_SECRET'])
    twitter_auth.set_access_token(
        os.environ['TWITTER_APP_TOKEN_KEY'],
        os.environ['TWITTER_APP_TOKEN_SECRET'])
    twitter_api = tweepy.API(twitter_auth)
    twitter_user = twitter_api.me()
    print_stdout('Logged in as @%s' % twitter_user.screen_name)
    vid_tweet = VideoTweet(twitter_api)

    queue_service = QueueService(
        account_name=os.environ['AZURE_STORAGE_ACCOUNT_NAME'],
        account_key=os.environ['AZURE_STORAGE_ACCOUNT_KEY']
    )

    queue_service.create_queue(queue_name)
    queue_service.create_queue(fail_queue_name)
    print_stdout('Created queue %s' % queue_name)
    print_stdout('Start poll loop')
    while run:
        for message in queue_service.get_messages(queue_name, num_messages=1):
            try:
                content = base64.b64decode(message.content)
                data = json.loads(content)
                filename = generate_mp4_file(data, yd, fps)
                if filename is not None:
                    status = vid_tweet.tweet(filename, **data['tweet'])
                    print_stdout('Sent tweet with media: "%s" - %s' % (
                        data['tweet']['status'],
                        status_url(status)
                    ))
                else:
                    status = twitter_api.update_status(**data['tweet'])
                    print_stdout('Sent tweet: "%s" - %s' % (
                        data['tweet']['status'],
                        status_url(status)
                    ))
            except:
                traceback.print_exc()
                print_stderr('Message was: %s' % content)
                queue_service.put_message(fail_queue_name, message.content)
            queue_service.delete_message(queue_name, message.id, message.pop_receipt)
        time.sleep(1)

if __name__ == "__main__":
    main()
