# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-20 04:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_grid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitycard',
            name='important',
            field=models.BooleanField(default=False),
        ),
    ]
