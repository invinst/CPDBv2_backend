from django.db import migrations


def create_initial_toast_template(apps, schema_editor):
    Toast = apps.get_model('toast', 'Toast')
    Toast.objects.get_or_create(
        name='OFFICER',
        defaults={
            'template': '**{rank} {full_name}** {age} {race} {gender},'
                        '\nwith *{complaint_count} complaints*, *{sustained_count} sustained* {action_type}.',
            'tags': '{rank} {full_name} {birth_year} {gender} {race} {complaint_count} {sustained_count} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='CR',
        defaults={
            'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.',
            'tags': '{crid} {category} {incident_date} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='TRR',
        defaults={
            'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.',
            'tags': '{id} {force_type} {incident_date}'
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('toast', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_toast_template,
        )
    ]
