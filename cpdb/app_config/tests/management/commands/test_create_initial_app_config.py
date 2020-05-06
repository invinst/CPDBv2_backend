from django.core.management import call_command
from django.test import TestCase
from robber import expect

from app_config.models import AppConfig
from app_config.constants import APP_CONFIG


class CreateInitialAppConfigCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('create_initial_app_config')
        config_objects = AppConfig.objects.all()
        expect(config_objects.count()).to.eq(len(APP_CONFIG))

        for config_data in APP_CONFIG:
            config_object = config_objects.filter(name=config_data['name']).first()
            expect(config_object).not_to.be.none()
            expect(config_object.name).to.eq(config_data['name'])
            expect(config_object.value).to.eq(config_data['value'])
            expect(config_object.description).to.eq(config_data['description'])
