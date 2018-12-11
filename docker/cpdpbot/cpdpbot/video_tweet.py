import os
import time

import requests
from tweepy.parsers import JSONParser
from tweepy.error import TweepError, RateLimitError, is_rate_limit_error_message
from tweepy.models import Status


MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'


class VideoTweet(object):
    def __init__(self, api):
        self.api = api
        self.oauth = self.api.auth.apply_auth()

    def post(self, url, data=None, json=None, **kwargs):
        kwargs['auth'] = self.oauth
        response = requests.post(url=url, data=data, json=json, **kwargs)

        if response.status_code and not 200 <= response.status_code < 300:
            try:
                error_msg, api_error_code = \
                    JSONParser().parse_error(response.text)
            except Exception:
                error_msg = "Twitter error response: status code = %s" % response.status_code
                api_error_code = None

            if is_rate_limit_error_message(error_msg):
                raise RateLimitError(error_msg, response)
            else:
                raise TweepError(error_msg, response, api_code=api_error_code)

        return response

    def upload_init(self, file_path):
        total_bytes = os.path.getsize(file_path)
        request_data = {
            'command': 'INIT',
            'media_type': 'video/mp4',
            'total_bytes': total_bytes,
            'media_category': 'tweet_video'
        }

        req = self.post(url=MEDIA_ENDPOINT_URL, data=request_data)
        media_id = req.json()['media_id']

        return media_id

    def upload_append(self, file_path, media_id):
        segment_id = 0
        bytes_sent = 0
        total_bytes = os.path.getsize(file_path)
        file = open(file_path, 'rb')

        while bytes_sent < total_bytes:
            chunk = file.read(4*1024*1024)

            request_data = {
                'command': 'APPEND',
                'media_id': media_id,
                'segment_index': segment_id
            }

            files = {
                'media': chunk
            }

            self.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files)

            segment_id = segment_id + 1
            bytes_sent = file.tell()

    def check_status(self, media_id, processing_info):
        if processing_info is None:
            return

        state = processing_info['state']
        if state == u'succeeded':
            return

        if state == u'failed':
            raise TweepError("Uploading video has failed.")

        check_after_secs = processing_info['check_after_secs']
        time.sleep(check_after_secs)

        request_params = {
            'command': 'STATUS',
            'media_id': media_id
        }

        req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=self.oauth)

        processing_info = req.json().get('processing_info', None)
        self.check_status(media_id, processing_info)

    def upload_finalize(self, media_id):
        request_data = {
            'command': 'FINALIZE',
            'media_id': media_id
        }

        req = self.post(url=MEDIA_ENDPOINT_URL, data=request_data)

        processing_info = req.json().get('processing_info', None)
        self.check_status(media_id, processing_info)

    def post_tweet(self, media_id, status, in_reply_to_status_id):
        request_data = {
            'status': status,
            'media_ids': media_id,
            'in_reply_to_status_id': in_reply_to_status_id
        }

        req = self.post(
            url=POST_TWEET_URL,
            data={
                key: val for key, val in request_data.items()
                if val is not None
            })
        return Status.parse(self.api, req.json())

    def tweet(self, file_path, status, in_reply_to_status_id=None):
        media_id = self.upload_init(file_path)
        self.upload_append(file_path, media_id)
        self.upload_finalize(media_id)
        return self.post_tweet(media_id, status, in_reply_to_status_id)
