# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-30 07:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0046_set_allegation_areas_lineareas'),
    ]

    operations = [
        migrations.AddField(
            model_name='officerallegation',
            name='disciplined',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='officerallegation',
            name='final_outcome',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='officerallegation',
            name='recc_outcome',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]