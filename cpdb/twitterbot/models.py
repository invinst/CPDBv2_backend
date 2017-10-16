from django.db import models


TYPE_SINGLE_OFFICER = 'single_officer'
TYPE_COACCUSED_PAIR = 'coaccused_pair'
TYPE_NOT_FOUND = 'not_found'
TYPE_CHOICES = [
    [TYPE_SINGLE_OFFICER, 'Single Officer'],
    [TYPE_COACCUSED_PAIR, 'Coaccused Pair'],
    [TYPE_NOT_FOUND, 'Not Found']
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


class TweetResponseRoundRobinManager(models.Manager):
    def get_template(self, username, response_type):
        templates = ResponseTemplate.objects.filter(response_type=response_type).order_by('id')
        response_round_robin, created = self.get_or_create(username=username, response_type=response_type)
        if not created:
            response_round_robin.last_index += 1

            if response_round_robin.last_index >= templates.count():
                response_round_robin.last_index = 0

            response_round_robin.save()
        return templates[response_round_robin.last_index]


class TweetResponseRoundRobin(models.Model):
    username = models.CharField(max_length=15)
    response_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    last_index = models.PositiveIntegerField(default=0)
    objects = TweetResponseRoundRobinManager()
