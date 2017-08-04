class Tweet:
    def __init__(self, original_tweet, client=None):
        self._original_tweet = original_tweet
        self._client = client
        self._in_reply_to_tweet = None
        self._retweeted_tweet = None
        self._quoted_tweet = None

    @property
    def text(self):
        return self._original_tweet.text

    @property
    def urls(self):
        screen_name = self._client.get_current_user().screen_name
        return [
            url['expanded_url']
            for url in self._original_tweet.entities.get('urls', []) if screen_name not in url['expanded_url']
        ]

    @property
    def hashtags(self):
        return [hashtag['text'] for hashtag in self._original_tweet.entities.get('hashtags', [])]

    @property
    def id(self):
        return self._original_tweet.id

    @property
    def user_id(self):
        return self._original_tweet.user.id

    @property
    def screen_name(self):
        return self._original_tweet.user.screen_name

    @property
    def user_mention_screen_names(self):
        return [mention['screen_name'] for mention in self._original_tweet.entities['user_mentions']]

    @property
    def in_reply_to_tweet(self):
        if self._in_reply_to_tweet:
            return self._in_reply_to_tweet
        if getattr(self._original_tweet, 'in_reply_to_tweet_id', None):
            self._in_reply_to_tweet = Tweet(
                self._client.get_tweet(self._original_tweet.in_reply_to_tweet_id), self._client
            )
            return self._in_reply_to_tweet
        return None

    @property
    def retweeted_tweet(self):
        if self._retweeted_tweet:
            return self._retweeted_tweet
        if getattr(self._original_tweet, 'retweeted_tweet', None):
            self._retweeted_tweet = Tweet(self._original_tweet.retweeted_tweet, self._client)
            return self._retweeted_tweet
        return None

    @property
    def quoted_tweet(self):
        if self._quoted_tweet:
            return self._quoted_tweet
        if getattr(self._original_tweet, 'quoted_tweet', None):
            self._quoted_tweet = Tweet(self._original_tweet.quoted_tweet, self._client)
            return self._quoted_tweet
        if getattr(self._original_tweet, 'quoted_tweet_id', None):
            self._quoted_tweet = Tweet(self._client.get_tweet(self._original_tweet.quoted_tweet_id), self._client)
            return self._quoted_tweet
        return None

    @property
    def is_retweet(self):
        return getattr(self._original_tweet, 'retweeted_tweet', None) is not None
