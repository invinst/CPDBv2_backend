from django.contrib.postgres.fields import JSONField
from django.db import models


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
    original_event_object = JSONField(null=True)
    status = models.CharField(max_length=10, choices=status_choices, default=PENDING)

    def __str__(self):
        return self.tweet_content
