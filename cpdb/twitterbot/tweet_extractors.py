class RelatedTweetExtractor(object):
    def extract(self, tweet, context):
        tweets = self.get_tweets(tweet, context)
        try:
            context['first_non_retweet'] = [t for t in tweets if not t.is_retweet][0]
        except IndexError:
            context['first_non_retweet'] = None
        context['original_tweet'] = self.get_original_tweet(tweets)
        return tweets

    def is_self_tweet(self, tweet, context):
        return tweet.user_id == context['for_user_id']

    def is_valid_tweet(self, tweet, context):
        return tweet is not None and not self.is_self_tweet(tweet, context)

    def get_tweets(self, tweet, context):
        if not self.is_valid_tweet(tweet, context):
            return []
        tweets = [tweet]
        tweets += self.get_related_tweets(tweet, context)
        return tweets

    def get_related_tweets(self, tweet, context):
        tweets = []
        tweets += self.get_tweets(tweet.in_reply_to_tweet, context)
        tweets += self.get_tweets(tweet.retweeted_status, context)
        tweets += self.get_tweets(tweet.quoted_tweet, context)
        return tweets

    def get_original_tweet(self, tweets):
        if len(tweets) > 0:
            return min(tweets, key=lambda tweet: tweet.created_at)


class DirectMentionTweetExtractor(RelatedTweetExtractor):
    def is_valid_tweet(self, tweet, context):
        return super(DirectMentionTweetExtractor, self).is_valid_tweet(tweet, context) \
            and tweet.is_mentioning_twitterbot
