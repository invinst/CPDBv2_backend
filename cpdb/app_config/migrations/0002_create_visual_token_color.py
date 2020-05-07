# Generated by Django 2.2.9 on 2020-04-13 08:37

import app_config.validators.visual_token_color_validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_config', '0001_create_app_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualTokenColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('color', models.CharField(max_length=7, validators=[app_config.validators.visual_token_color_validators.is_valid_hex_color])),
                ('text_color', models.CharField(max_length=7, validators=[app_config.validators.visual_token_color_validators.is_valid_hex_color])),
                ('lower_range', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('upper_range', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
