# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-27 07:54
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_officer_rank_increase_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='officer',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, null=True), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='policeunit',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
