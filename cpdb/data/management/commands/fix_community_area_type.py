from django.core.management import BaseCommand

from data.models import Area


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for area in Area.objects.filter(area_type='Community'):
            area.area_type = 'community'
            area.name = area.name.title()
            area.save()
