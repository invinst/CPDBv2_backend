# Generated by Django 2.1.3 on 2019-01-04 02:19

from django.db import migrations

from email_service.constants import (
    CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE, TRR_ATTACHMENT_REQUEST, TRR_ATTACHMENT_AVAILABLE,
)


def create_initial_email_template(apps, schema_editor):
    EmailTemplate = apps.get_model('email_service', 'EmailTemplate')
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


def remove_initial_email_template(apps, schema_editor):
    EmailTemplate = apps.get_model('email_service', 'EmailTemplate')
    templates = EmailTemplate.objects.filter(type__in=[
        CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE, TRR_ATTACHMENT_REQUEST, TRR_ATTACHMENT_AVAILABLE
    ])
    templates.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('email_service', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_email_template,
            reverse_code=remove_initial_email_template,
        ),
    ]
