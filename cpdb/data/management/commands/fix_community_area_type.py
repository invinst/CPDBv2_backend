from django.core.management import BaseCommand

from data.models import Area


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Area.objects.filter(area_type='Community').update(area_type='community')
