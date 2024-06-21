# Generated by Django 2.2.10 on 2024-06-10 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0131_auto_20240609_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='officerallegation',
            name='recc_finding',
            field=models.CharField(blank=True, choices=[['UN', 'Unfounded'], ['EX', 'Exonerated'], ['NS', 'Not Sustained'], ['SU', 'Sustained'], ['NC', 'No Cooperation'], ['NA', 'No Affidavit'], ['DS', 'Discharged'], ['ZZ', 'Unknown']], max_length=30),
        ),
    ]