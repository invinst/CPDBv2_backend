# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-09 08:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0006_re_add_storypage_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storypage',
            name='post_date',
            field=models.DateField(null=True),
        ),
    ]
