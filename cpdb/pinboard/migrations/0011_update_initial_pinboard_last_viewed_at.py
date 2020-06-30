from __future__ import unicode_literals
from django.db import migrations, models


def update_initial_pinboard_last_viewed_at(apps, schema_editor):
    Pinboard = apps.get_model('pinboard', 'Pinboard')
    pinboards = Pinboard.objects.all()
    for pinboard in pinboards:
        pinboard.last_viewed_at = pinboard.updated_at
    Pinboard.objects.bulk_update(pinboards, ['last_viewed_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('pinboard', '0010_pinboard_last_viewed_at'),
    ]

    operations = [
        migrations.RunPython(
            update_initial_pinboard_last_viewed_at,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
