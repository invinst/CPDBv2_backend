from django.db import models


class DocumentCrawler(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)
