# Generated by Django 2.1.3 on 2019-01-04 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0098_attachmentfile_text_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachmentrequest',
            name='noti_email_sent',
            field=models.BooleanField(default=False, verbose_name='Notification email sent'),
        ),
    ]