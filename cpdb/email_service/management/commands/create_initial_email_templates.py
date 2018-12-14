from django.core.management.base import BaseCommand

from email_service.models import EmailTemplate
from email_service.constants import (
    CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE, TRR_ATTACHMENT_REQUEST,
    TRR_ATTACHMENT_AVAILABLE,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        EmailTemplate.objects.get_or_create(
            type=CR_ATTACHMENT_REQUEST,
            defaults={
                'subject': 'Allegation document request success',
                'body': '''Dear **{name}**,

Your document request for allegation {pk} has been recorded.
We will send an email to you when any new document is available.

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )

        EmailTemplate.objects.get_or_create(
            type=CR_ATTACHMENT_AVAILABLE,
            defaults={
                'subject': 'Allegation document for {pk} now available',
                'body': '''Dear **{name}**,

There are new documents for allegation {pk}.
To see them, please go to {url}

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )

        EmailTemplate.objects.get_or_create(
            type=TRR_ATTACHMENT_REQUEST,
            defaults={
                'subject': 'TRR document request success',
                'body': '''Dear **{name}**,

Your document request for TRR {pk} has been recorded.
We will send an email to you when any new document is available.

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )

        EmailTemplate.objects.get_or_create(
            type=TRR_ATTACHMENT_AVAILABLE,
            defaults={
                'subject': 'TRR document for {pk} now available',
                'body': '''Dear **{name}**,

There are new documents for TRR {pk}.
To see them, please go to {url}

Regards,
CPDP team''',
                'from_email': 'info@cpdp.co'
            }
        )
