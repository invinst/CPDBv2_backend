from django.db import models


TYPE_CHOICES = [
    ['single_officer', 'Single Officer'],
    ['coaccused_pair', 'Coaccused Pair'],
    ['not_found', 'Not Found']
]


class ResponseTemplate(models.Model):
    response_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    syntax = models.TextField()
