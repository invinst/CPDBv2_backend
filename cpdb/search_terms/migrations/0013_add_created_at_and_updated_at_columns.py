# Generated by Django 2.1.3 on 2018-12-14 04:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('search_terms', '0012_alter_searchtermitem_call_to_action_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchtermcategory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='searchtermcategory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='searchtermitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='searchtermitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]