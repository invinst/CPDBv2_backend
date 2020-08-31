# Generated by Django 2.2.10 on 2020-06-17 06:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('data', '0124_attachmentnarrative'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachmentfile',
            name='owner_id',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='attachmentfile',
            name='owner_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]