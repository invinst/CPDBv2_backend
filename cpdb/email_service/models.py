from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
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

    def create_message(self, to, cc, **kwargs):
        html_message = markdown(self.body.format(**kwargs), extras=['break-on-newline', 'cuddled-lists', 'tables'])
        email = EmailMultiAlternatives(
            subject=self.subject.format(**kwargs),
            body=strip_tags(html_message),
            from_email=self.from_email,
            to=to,
            cc=cc,
        )
        email.attach_alternative(html_message, 'text/html')
        return email
