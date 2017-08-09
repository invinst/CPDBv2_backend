from .models import TwitterBotResponseLog
from .tweets import Tweet


class DatabaseResponseLogger:
    def log_response(self, response, outgoing_tweet, context):
        sources, tweet_content, entity_url = response
        original_tweet = context['original_tweet']
        incoming_tweet = context['incoming_tweet']
        response_log = TwitterBotResponseLog(
            sources=', '.join(sources),
            entity_url=entity_url,
            tweet_content=tweet_content,
            tweet_url=Tweet(outgoing_tweet).url,
            incoming_tweet_username=incoming_tweet.screen_name,
            incoming_tweet_url=incoming_tweet.url,
            incoming_tweet_content=incoming_tweet.text,
            original_tweet_username=original_tweet.screen_name,
            original_tweet_url=original_tweet.url,
            original_tweet_content=original_tweet.text)

        response_log.save()
