# Generated by Django 2.2.10 on 2020-08-14 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0010_remove_lawsuit_plaintiff_unique_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawsuit',
            name='airtable_id',
            field=models.CharField(db_index=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='airtable_updated_at',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='lawsuitplaintiff',
            name='airtable_id',
            field=models.CharField(db_index=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='lawsuitplaintiff',
            name='airtable_updated_at',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='airtable_id',
            field=models.CharField(db_index=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='airtable_updated_at',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_date',
            field=models.DateTimeField(null=True),
        ),
    ]
