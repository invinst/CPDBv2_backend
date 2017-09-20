from django.db import models


class ActivityCard(models.Model):
    officer = models.OneToOneField('data.Officer', on_delete=models.CASCADE, related_name='activity_card')
    important = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True)
