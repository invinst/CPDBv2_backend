from tweepy import TweepError

TWITTER_USER_NOT_FOUND_ERROR = 50
TWITTER_TWEET_NOT_FOUND_ERROR = 144
TWITTER_ACCOUNT_SUSPENDED_ERROR = 64


class DictObject(object):
    def __init__(self, data):
        self.raw_data = data

        for key, value in data.items():
            setattr(self, key, value)


class TweepyWrapper(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client
        self._current_user = None
        self._user_dict = {}

    @property
    def tweepy_api(self):
        return self._client

    def get_current_user(self):
        if self._current_user is None:
            self._current_user = DictObject(self._client.me()._json)
        return self._current_user

    def get_user(self, id):
        if id in self._user_dict:
            return self._user_dict[id]

        try:
            user = DictObject(self._client.get_user(user_id=id)._json)
            self._user_dict[id] = user
            return user
        except TweepError as e:
            if e.api_code == TWITTER_USER_NOT_FOUND_ERROR:
                return None
            raise

    def unfollow(self, user_id):
        return DictObject(self._client.destroy_friendship(user_id=user_id)._json)

    def follow(self, user_id, notify=False):
        try:
            return DictObject(self._client.create_friendship(user_id=user_id, follow=notify)._json)
        except TweepError as e:
            if e.api_code == TWITTER_ACCOUNT_SUSPENDED_ERROR:
                return self.get_user(user_id)
            raise

    def get_tweet(self, id):
        try:
            return DictObject(self._client.get_status(id=id)._json)
        except TweepError as e:
            if e.api_code == TWITTER_TWEET_NOT_FOUND_ERROR:
                return None
            raise
