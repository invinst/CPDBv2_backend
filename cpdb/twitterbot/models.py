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
    PENDING = 'PENDING'
    SENT = 'SENT'
    status_choices = (
        (PENDING, 'Pending'),
        (SENT, 'Sent')
    )

    sources = models.TextField()
    entity_url = models.URLField(blank=True)
    tweet_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tweet_url = models.URLField(blank=True)
    incoming_tweet_username = models.CharField(max_length=15)
    incoming_tweet_url = models.URLField()
    incoming_tweet_content = models.TextField()
    original_tweet_username = models.CharField(max_length=15)
    original_tweet_url = models.URLField()
    original_tweet_content = models.TextField()
    status = models.CharField(max_length=10, choices=status_choices, default=PENDING)
