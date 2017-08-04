from django.db import models


TYPE_CHOICES = [
    ['single_officer', 'Single Officer'],
    ['coaccused_pair', 'Coaccused Pair'],
    ['not_found', 'Not Found']
]


class ResponseTemplate(models.Model):
    response_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    syntax = models.TextField()


class TwitterBotResponseLog(models.Model):
    sources = models.TextField()
    entity_url = models.URLField()
    tweet_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tweet_url = models.URLField()
    incoming_tweet_username = models.CharField(max_length=15)
    incoming_tweet_url = models.URLField()
    incoming_tweet_content = models.TextField()
    original_tweet_username = models.CharField(max_length=15, blank=True)
    original_tweet_url = models.URLField(blank=True)
    original_tweet_content = models.TextField(blank=True)
