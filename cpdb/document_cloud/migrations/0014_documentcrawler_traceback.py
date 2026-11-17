from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_cloud', '0013_add_document_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentcrawler',
            name='traceback',
            field=models.TextField(null=True, blank=True),
        ),
    ]
