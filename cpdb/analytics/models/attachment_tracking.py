from django.contrib.gis.db import models


class AttachmentTracking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    attachment_file = models.ForeignKey('data.AttachmentFile', on_delete=models.CASCADE, null=False)
    accessed_from_page = models.CharField(max_length=50)
    app = models.CharField(max_length=50)
