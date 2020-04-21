from django.core.management.base import BaseCommand
from app_config.models import AppConfig
from app_config.constants import APP_CONFIG


class Command(BaseCommand):
    def handle(self, *args, **options):
        for config_data in APP_CONFIG:
            config_object = AppConfig.objects.filter(name=config_data['name']).first()
            if not config_object:
                AppConfig.objects.create(**config_data)
