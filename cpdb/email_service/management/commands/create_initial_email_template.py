from django.core.management.base import BaseCommand

from email_service.models import EmailTemplate
from email_service.constants import ATTACHMENT_REQUEST, ATTACHMENT_AVAILABLE


class Command(BaseCommand):
    def handle(self, *args, **options):
        EmailTemplate.objects.get_or_create(
            type=ATTACHMENT_REQUEST,
            defaults={
                'subject': 'Document request success',
                'body': (
                    'Dear citizen,\n\n'
                    '\tWe received your document request for allegation {crid}. '
                    'We will send an email to you when any document is available.\n\n'
                    'Thank you!\nCPDP team'
                ),
                'from_email': 'info@cpdp.co'
            }
        )
        EmailTemplate.objects.get_or_create(
            type=ATTACHMENT_AVAILABLE,
            defaults={
                'subject': 'Document for {crid} now available',
                'body': (
                    'Dear citizen,\n\n'
                    'We have new documents for allegation {crid}. '
                    'To see them, please go to {cr_page_url}.\n\n'
                    'Sincerely!\nCPDP team'
                ),
                'from_email': 'info@cpdp.co'
            }
        )
