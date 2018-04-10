# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-28 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0031_remove_policewitness_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TRR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beat', models.PositiveSmallIntegerField(null=True)),
                ('block', models.CharField(max_length=8, null=True)),
                ('direction', models.CharField(choices=[(b'West', b'West'), (b'North', b'North'), (b'South', b'South'), (b'East', b'East')], max_length=8, null=True)),
                ('street', models.CharField(max_length=64, null=True)),
                ('location', models.CharField(max_length=64, null=True)),
                ('trr_datetime', models.DateTimeField(null=True)),
                ('indoor_or_outdoor', models.CharField(choices=[(b'Indoor', b'Indoor'), (b'Outdoor', b'Outdoor')], max_length=8, null=True)),
                ('lighting_condition', models.CharField(choices=[(b'DAYLIGHT', b'Daylight'), (b'GOOD ARTIFICIAL', b'Good Artificial'), (b'DUSK', b'Dusk'), (b'NIGHT', b'Night'), (b'POOR ARTIFICIAL', b'Poor Artificial'), (b'DAWN', b'Dawn')], max_length=32, null=True)),
                ('weather_condition', models.CharField(choices=[(b'OTHER', b'Other'), (b'CLEAR', b'Clear'), (b'SNOW', b'Snow'), (b'RAIN', b'Rain'), (b'SLEET/HAIL', b'Sleet/hail'), (b'SEVERE CROSS WIND', b'Severe Cross Wind'), (b'FOG/SMOKE/HAZE', b'Fog/smoke/haze')], max_length=32, null=True)),
                ('notify_OEMC', models.NullBooleanField()),
                ('notify_district_sergeant', models.NullBooleanField()),
                ('notify_OP_command', models.NullBooleanField()),
                ('notify_DET_division', models.NullBooleanField()),
                ('number_of_weapons_discharged', models.PositiveSmallIntegerField(null=True)),
                ('party_fired_first', models.CharField(choices=[(b'MEMBER', b'Member'), (b'OTHER', b'Other'), (b'OFFENDER', b'Offender')], max_length=16, null=True)),
                ('location_recode', models.CharField(max_length=64, null=True)),
                ('taser', models.NullBooleanField()),
                ('total_number_of_shots', models.PositiveSmallIntegerField(null=True)),
                ('firearm_used', models.NullBooleanField()),
                ('number_of_officers_using_firearm', models.PositiveSmallIntegerField(null=True)),
                ('officer_assigned_beat', models.CharField(max_length=16, null=True)),
                ('officer_duty_status', models.NullBooleanField()),
                ('officer_in_uniform', models.NullBooleanField()),
                ('officer_injured', models.NullBooleanField()),
                ('officer_rank', models.CharField(max_length=32, null=True)),
                ('subject_id', models.PositiveSmallIntegerField(null=True)),
                ('subject_armed', models.NullBooleanField()),
                ('subject_injured', models.NullBooleanField()),
                ('subject_alleged_injury', models.NullBooleanField()),
                ('subject_age', models.PositiveSmallIntegerField(null=True)),
                ('subject_birth_year', models.PositiveSmallIntegerField(null=True)),
                ('subject_gender', models.CharField(choices=[[b'M', b'Male'], [b'F', b'Female'], [b'X', b'X']], max_length=1, null=True)),
                ('subject_race', models.CharField(max_length=32, null=True)),
                ('officer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Officer')),
            ],
        ),
    ]