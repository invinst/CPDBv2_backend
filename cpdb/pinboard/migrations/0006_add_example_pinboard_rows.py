from django.db import migrations


def add_example_pinboard_rows(apps, schema_editor):
    Pinboard = apps.get_model('pinboard', 'Pinboard')
    skullcal_pinboard = Pinboard.objects.get(id='22e66085')
    watts_pinboard = Pinboard.objects.get(id='b20c2c36')

    ExamplePinboard = apps.get_model('pinboard', 'ExamplePinboard')
    ExamplePinboard.objects.create(pinboard=skullcal_pinboard)
    ExamplePinboard.objects.create(pinboard=watts_pinboard)


class Migration(migrations.Migration):

    dependencies = [
        ('pinboard', '0005_examplepinboard'),
    ]

    operations = [
        migrations.RunPython(
            add_example_pinboard_rows,
            reverse_code=migrations.RunPython.noop,
            elidable=True
        ),
    ]
