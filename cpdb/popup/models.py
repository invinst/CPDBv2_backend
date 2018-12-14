from django.db import models


class Popup(models.Model):
    name = models.CharField(max_length=64)
    page = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
