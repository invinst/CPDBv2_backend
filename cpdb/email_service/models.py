from django.utils.html import strip_tags
from markdown2 import markdown

from django.db import models

from email_service.constants import ATTACHMENT_TYPE_CHOICES


class EmailTemplate(models.Model):
    type = models.CharField(
        choices=ATTACHMENT_TYPE_CHOICES,
        max_length=255
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField(max_length=255)

    def create_message(self, recipient_list, **kwargs):
        html_message = markdown(self.body.format(**kwargs))
        return {
            'subject': self.subject.format(**kwargs),
            'message': strip_tags(html_message),
            'html_message': html_message,
            'from_email': self.from_email,
            'recipient_list': recipient_list
        }
