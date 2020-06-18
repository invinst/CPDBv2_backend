from __future__ import unicode_literals
from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType


def migrate_from_attachment_allegation_to_owner(apps, schema_editor):
    AttachmentFile = apps.get_model('data', 'AttachmentFile')
    Allegation = apps.get_model('data', 'Allegation')
    attachment_files = AttachmentFile.objects.all().select_related('allegation')

    allegation_content_type = ContentType.objects.get_for_model(Allegation)
    for attachment in attachment_files:
        attachment.owner_id = attachment.allegation_id
        attachment.owner_type_id = allegation_content_type.id

    AttachmentFile.objects.bulk_update(attachment_files, ['owner_id', 'owner_type_id'], batch_size=10000)


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0122_add_owner_data'),
    ]

    operations = [
        migrations.RunPython(
            migrate_from_attachment_allegation_to_owner,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
