# Generated by Django 2.2.10 on 2024-08-09 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trr', '0021_auto_20240610_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trr',
            name='lighting_condition',
            field=models.CharField(choices=[('DAYLIGHT', 'Daylight'), ('DAY', 'Daylight'), ('GOOD ARTIFICIAL', 'Good Artificial'), ('ARTIFICIAL', 'Artificial'), ('ART', 'Artificial'), ('DARKNESS', 'Darkness'), ('DAR', 'Darkness'), ('DUSK', 'Dusk'), ('NIGHT', 'Night'), ('POOR ARTIFICIAL', 'Poor Artificial'), ('DAWN', 'Dawn')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='trr',
            name='weather_condition',
            field=models.CharField(choices=[('OTHER', 'Other'), ('CLEAR', 'Clear'), ('SNOW', 'Snow'), ('RAIN', 'Rain'), ('CLOUD', 'Cloud'), ('SLEET/HAIL', 'Sleet/hail'), ('SEVERE CROSS WIND', 'Severe Cross Wind'), ('FOG/SMOKE/HAZE', 'Fog/smoke/haze'), ('FOG', 'Fog/smoke/haze')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='weapondischarge',
            name='object_struck_of_discharge',
            field=models.CharField(choices=[('OBJECT', 'OBJECT'), ('PERSON', 'PERSON'), ('UNKNOWN', 'UNKNOWN'), ('BOTH', 'BOTH'), ('ANIMAL', 'ANIMAL')], max_length=32, null=True),
        ),
    ]