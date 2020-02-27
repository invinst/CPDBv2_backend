from django.db import migrations


def create_initial_toast_template(apps, schema_editor):
    Toast = apps.get_model('toast', 'Toast')
    Toast.objects.get_or_create(
        name='MOBILE OFFICER',
        defaults={
            'template': '{full_name} {action_type} pinboard',
            'tags': '{full_name} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='MOBILE CR',
        defaults={
            'template': 'CR #{crid} {action_type} pinboard',
            'tags': '{crid} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='MOBILE TRR',
        defaults={
            'template': 'TRR #{id} {action_type} pinboard',
            'tags': '{id} {action_type}'
        }
    )


def remove_initial_toast_template(apps, schema_editor):
    Toast = apps.get_model('toast', 'Toast')
    templates = Toast.objects.filter(name__in=['MOBILE OFFICER', 'MOBILE CR', 'MOBILE TRR'])
    templates.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('toast', '0002_create_initial_toast_template'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_toast_template,
            reverse_code=remove_initial_toast_template,
        )
    ]
