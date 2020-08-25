# Generated by Django 2.2.10 on 2020-08-17 09:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0003_lawsuit_primary_cause'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawsuit',
            name='interactions',
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='interactions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None),
        ),
        migrations.RemoveField(
            model_name='lawsuit',
            name='misconducts',
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='misconducts',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None),
        ),
        migrations.RemoveField(
            model_name='lawsuit',
            name='outcomes',
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='outcomes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None),
        ),
        migrations.RemoveField(
            model_name='lawsuit',
            name='services',
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='services',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None),
        ),
        migrations.RemoveField(
            model_name='lawsuit',
            name='violences',
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='violences',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None),
        ),
        migrations.DeleteModel(
            name='LawsuitInteraction',
        ),
        migrations.DeleteModel(
            name='LawsuitMisconduct',
        ),
        migrations.DeleteModel(
            name='LawsuitOutcome',
        ),
        migrations.DeleteModel(
            name='LawsuitService',
        ),
        migrations.DeleteModel(
            name='LawsuitViolence',
        ),
    ]
