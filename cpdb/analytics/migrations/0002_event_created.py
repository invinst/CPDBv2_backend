# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-23 05:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 1, 22, 23, 9, 9, 684328)),
            preserve_default=False,
        ),
    ]
