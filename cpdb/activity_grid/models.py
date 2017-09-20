from django.db import models


class ActivityCard(models.Model):
    officer = models.OneToOneField('data.Officer', on_delete=models.CASCADE)
