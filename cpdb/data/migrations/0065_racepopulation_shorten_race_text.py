# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-12 04:35
from __future__ import unicode_literals

from django.db import migrations


def alter_data(apps, schema_editor):
    RacePopulation = apps.get_model('data', 'RacePopulation')
    RacePopulation.objects.filter(race='Black or African-American').update(race='Black')
    RacePopulation.objects.filter(race='Persons of Spanish Language').update(race='Hispanic')


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0064_set_allegation_areas_lineareas'),
    ]

    operations = [
        migrations.RunPython(
            alter_data,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
