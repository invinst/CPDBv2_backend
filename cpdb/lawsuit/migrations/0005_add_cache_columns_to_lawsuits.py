# Generated by Django 2.2.10 on 2020-08-26 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawsuit', '0004_change_to_array_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawsuit',
            name='total_legal_fees',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True),
        ),
        migrations.AddField(
            model_name='lawsuit',
            name='total_settlement',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True),
        ),
    ]
