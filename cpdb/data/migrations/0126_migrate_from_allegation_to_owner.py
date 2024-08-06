from __future__ import unicode_literals
from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType
from django.db.models import F


def migrate_from_attachment_allegation_to_owner(apps, schema_editor):
    AttachmentFile = apps.get_model('data', 'AttachmentFile')
    Allegation = apps.get_model('data', 'Allegation')
    allegation_content_type = ContentType.objects.get_for_model(Allegation)
    AttachmentFile.objects.update(owner_id=F('allegation_id'), owner_type_id=allegation_content_type.id)


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0125_add_owner_data'),
    ]

    operations = [
        migrations.RunPython(
            migrate_from_attachment_allegation_to_owner,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
