from django.core.management.base import BaseCommand

from email_service.models import EmailTemplate
from email_service.constants import ATTACHMENT_REQUEST, ATTACHMENT_AVAILABLE


class Command(BaseCommand):
    def handle(self, *args, **options):
        EmailTemplate.objects.get_or_create(
            type=ATTACHMENT_REQUEST,
            defaults={
                'subject': 'Document request success',
                'body': '''Dear citizen,

Your document request for allegation {crid} has been recorded.
We will send an email to you when any new document is available.

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )
        EmailTemplate.objects.get_or_create(
            type=ATTACHMENT_AVAILABLE,
            defaults={
                'subject': 'Document for {crid} now available',
                'body': '''Dear citizen,

There are new documents for allegation {crid}.
To see them, please go to {cr_page_url}

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )
