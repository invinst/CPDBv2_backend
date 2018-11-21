# -*- coding: utf-8 -*-
from django.db import migrations


def rename_officer_rank(apps, schema_editor):
    Officer = apps.get_model('data', 'Officer')
    Officer.objects.filter(rank__iexact='po').update(rank='Police Officer')
    Officer.objects.filter(rank__iexact='det').update(rank='Detective')
    Salary = apps.get_model('data', 'Salary')
    Salary.objects.filter(rank__iexact='po').update(rank='Police Officer')
    Salary.objects.filter(rank__iexact='det').update(rank='Detective')


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0085_officer_has_unique_name'),
    ]

    operations = [
        migrations.RunPython(
            rename_officer_rank,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
