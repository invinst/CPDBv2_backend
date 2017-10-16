class TweetAuthorRecipientExtractor:
    def extract(self, tweets, context):
        screen_name = context['client'].get_current_user().screen_name
        return list(set([tweet.screen_name for tweet in tweets if tweet.screen_name != screen_name]))


class TweetMentionRecipientExtractor:
    def extract(self, tweets, context):
        screen_names = []
        screen_name = context['client'].get_current_user().screen_name
        for tweet in tweets:
            screen_names += tweet.user_mention_screen_names
        return filter(lambda name: name != screen_name, list(set(screen_names)))
