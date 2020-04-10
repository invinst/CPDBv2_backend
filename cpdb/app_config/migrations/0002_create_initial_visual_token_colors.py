from django.db import migrations


def create_initial_visual_token_colors(apps, schema_editor):
    VisualTokenColor = apps.get_model('app_config', 'VisualTokenColor')
    VisualTokenColor.objects.create(
        color='#F5F4F4',
        text_color='#231F20',
        lower_range=0,
        upper_range=10
    )
    VisualTokenColor.objects.create(
        color='#F9D3C3',
        text_color='#231F20',
        lower_range=10,
        upper_range=30
    )
    VisualTokenColor.objects.create(
        color='#F4A298',
        text_color='#231F20',
        lower_range=30,
        upper_range=70
    )
    VisualTokenColor.objects.create(
        color='#FF6453',
        text_color='#231F20',
        lower_range=70,
        upper_range=95
    )
    VisualTokenColor.objects.create(
        color='#FF412C',
        text_color='#231F20',
        lower_range=95,
        upper_range=99
    )
    VisualTokenColor.objects.create(
        color='#F52524',
        text_color='#ADADAD',
        lower_range=99,
        upper_range=100
    )


def remove_initial_visual_token_colors(apps, schema_editor):
    VisualTokenColor = apps.get_model('app_config', 'VisualTokenColor')
    VisualTokenColor.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app_config', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_visual_token_colors,
            reverse_code=remove_initial_visual_token_colors,
        )
    ]
