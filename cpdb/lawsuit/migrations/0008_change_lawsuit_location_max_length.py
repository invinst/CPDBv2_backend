# Generated by Django 2.2.10 on 2020-08-14 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0007_alter_officers_fields_in_lawsuits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawsuit',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
