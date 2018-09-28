from __future__ import print_function
import os
import sys
import json
import time
import traceback
import signal
import base64
import logging

import tweepy
from azure.storage.queue import QueueService

from .movie import write_mp4
from .video_tweet import VideoTweet


class TweetSender(object):
    run = True

    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.fps = int(os.environ.get('FPS', '40'))
        self.yd = float(os.environ.get('YEAR_DURATION', '0.5'))
        self.queue_name = os.environ['AZURE_QUEUE_NAME']
        self.fail_queue_name = '%sfail' % self.queue_name

        self.logger = logging.getLogger('main')

        twitter_auth = tweepy.OAuthHandler(
            os.environ['TWITTER_CONSUMER_KEY'],
            os.environ['TWITTER_CONSUMER_SECRET'])
        twitter_auth.set_access_token(
            os.environ['TWITTER_APP_TOKEN_KEY'],
            os.environ['TWITTER_APP_TOKEN_SECRET'])
        self.twitter_api = tweepy.API(twitter_auth)
        twitter_user = self.twitter_api.me()
        self.print_stdout('Logged in as @%s' % twitter_user.screen_name)
        self.vid_tweet = VideoTweet(self.twitter_api)

        self.queue_service = QueueService(
            account_name=os.environ['AZURE_STORAGE_ACCOUNT_NAME'],
            account_key=os.environ['AZURE_STORAGE_ACCOUNT_KEY']
        )

        self.queue_service.create_queue(self.queue_name)
        self.queue_service.create_queue(self.fail_queue_name)
        self.print_stdout('Created queue %s' % self.queue_name)

    def print_stdout(self, message):
        self.logger.info(message)
        print(message)
        sys.stdout.flush()

    def print_exception(self, message):
        self.logger.exception(message)
        traceback.print_exc()
        print(message, file=sys.stderr)
        sys.stderr.flush()

    def status_url(self, status):
        return 'https://twitter.com/%s/status/%s/' % (status.user.screen_name, status.id)

    def signal_handler(self, signal, frame):
        self.print_stdout('Exiting...')
        self.run = False

    def generate_mp4_file(self, data):
        if 'percentiles' in data:
            return write_mp4(data, self.yd, self.fps)
        return None

    def process_messages(self):
        for message in self.queue_service.get_messages(self.queue_name, num_messages=1):
            try:
                content = base64.b64decode(message.content).decode('utf-8')
                data = json.loads(content)
                filename = self.generate_mp4_file(data)
                if filename is not None:
                    status = self.vid_tweet.tweet(filename, **data['tweet'])
                    self.print_stdout('Sent status with media: %s - %s' % (
                        data['tweet']['status'],
                        self.status_url(status)
                    ))
                else:
                    status = self.twitter_api.update_status(**data['tweet'])
                    self.print_stdout('Sent status: %s - %s' % (
                        data['tweet']['status'],
                        self.status_url(status)
                    ))
            except Exception:
                self.print_exception('Cannot send status: %s' % content)
                self.queue_service.put_message(self.fail_queue_name, message.content)
            self.queue_service.delete_message(self.queue_name, message.id, message.pop_receipt)

    def run(self):
        self.print_stdout('Start poll loop')
        while self.run:
            self.process_messages()
            time.sleep(1)


if __name__ == "__main__":
    TweetSender().run()
