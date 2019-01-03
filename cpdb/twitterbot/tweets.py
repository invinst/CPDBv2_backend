from dateutil.parser import parse


class TweetContext(object):
    def __init__(self, original_tweet, context=None):
        self._original_tweet = original_tweet
        self._context = context
        self._in_reply_to_tweet = None
        self._retweeted_status = None
        self._quoted_status = None

    @property
    def text(self):
        return self._original_tweet.get('text')

    @property
    def urls(self):
        screen_name = self._context['client'].get_user(self._context['for_user_id']).screen_name
        return [
            url['expanded_url']
            for url in self._original_tweet.get('entities').get('urls', []) if screen_name not in url['expanded_url']
        ]

    @property
    def hashtags(self):
        return [hashtag['text'] for hashtag in self._original_tweet.get('entities').get('hashtags', [])]

    @property
    def id(self):
        return self._original_tweet.get('id')

    @property
    def user_id(self):
        return self._original_tweet.get('user', {}).get('id')

    @property
    def screen_name(self):
        return self._original_tweet.get('user', {}).get('screen_name')

    @property
    def user_mention_screen_names(self):
        return [mention['screen_name'] for mention in self._original_tweet.get('entities')['user_mentions']]

    @property
    def user_mention_ids(self):
        return [mention['id'] for mention in self._original_tweet.get('entities')['user_mentions']]

    @property
    def in_reply_to_tweet(self):
        if self._in_reply_to_tweet:
            return self._in_reply_to_tweet
        if self._original_tweet.get('in_reply_to_status_id'):
            self._in_reply_to_tweet = TweetContext(
                self._context['client'].get_tweet(self._original_tweet.get('in_reply_to_status_id')), self._context
            )
            return self._in_reply_to_tweet
        return None

    @property
    def retweeted_status(self):
        if self._retweeted_status:
            return self._retweeted_status
        if self._original_tweet.get('retweeted_status'):
            self._retweeted_status = TweetContext(self._original_tweet.get('retweeted_status'), self._context)
            return self._retweeted_status
        return None

    @property
    def quoted_status(self):
        if self._quoted_status:
            return self._quoted_status
        if self._original_tweet.get('quoted_status'):
            self._quoted_status = TweetContext(self._original_tweet.get('quoted_status'), self._context)
            return self._quoted_status
        if self._original_tweet.get('quoted_status_id'):
            self._quoted_status = TweetContext(
                self._context['client'].get_tweet(self._original_tweet.get('quoted_status_id')), self._context
            )
            return self._quoted_status
        return None

    @property
    def is_retweet(self):
        return self._original_tweet.get('retweeted_status') is not None

    @property
    def url(self):
        return f'https://twitter.com/{self.screen_name}/status/{self.id}/'

    @property
    def created_at(self):
        return parse(self._original_tweet.get('created_at'))

    @property
    def is_tweet_from_followed_accounts(self):
        _, target = self._context['client'].tweepy_api.show_friendship(
            source_id=self._context['for_user_id'], target_id=self.user_id)
        return target.followed_by

    @property
    def is_retweet_of_twitterbot(self):
        return self.retweeted_status is not None and self.retweeted_status.user_id == self._context['for_user_id']

    @property
    def is_quoted_tweet_of_twitterbot(self):
        return self.quoted_status is not None and self.quoted_status.user_id == self._context['for_user_id']

    @property
    def is_unfollow_tweet(self):
        bot = self._context['client'].get_user(self._context['for_user_id']).screen_name.lower()
        return self.text.strip().lower() == f'@{bot} stop'

    @property
    def is_mentioning_twitterbot(self):
        return self._context['for_user_id'] in self.user_mention_ids
