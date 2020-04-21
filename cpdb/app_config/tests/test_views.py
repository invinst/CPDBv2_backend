from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_config.factories import AppConfigFactory


class AppConfigTestCase(APITestCase):

    def test_should_return_correct_app_config(self):
        AppConfigFactory(name='CONFIG_1', value='VALUE 1')
        AppConfigFactory(name='CONFIG_2', value='VALUE 2')
        AppConfigFactory(name='CONFIG_3', value='VALUE 3')

        url = reverse('api-v2:app-config-list')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        app_config = response.data
        expect(len(app_config)).to.eq(3)
        expect(app_config).to.eq({
            'CONFIG_1': 'VALUE 1',
            'CONFIG_2': 'VALUE 2',
            'CONFIG_3': 'VALUE 3',
        })
