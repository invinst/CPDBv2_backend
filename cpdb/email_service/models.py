from markdown2 import markdown

from django.db import models
from .constants import ATTACHMENT_REQUEST, ATTACHMENT_AVAILABLE


class EmailTemplate(models.Model):
    type = models.CharField(
        choices=[(ATTACHMENT_REQUEST, ATTACHMENT_REQUEST), (ATTACHMENT_AVAILABLE, ATTACHMENT_AVAILABLE)],
        max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField(max_length=255)

    def create_message(self, to, **kwargs):
        return self.subject.format(**kwargs), markdown(self.body.format(**kwargs)), self.from_email, to
