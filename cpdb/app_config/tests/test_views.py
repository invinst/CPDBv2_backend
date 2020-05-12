from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_config.factories import AppConfigFactory, VisualTokenColorFactory


class AppConfigTestCase(APITestCase):
    def test_should_return_correct_app_config(self):
        AppConfigFactory(name='CONFIG_1', value='VALUE 1')
        AppConfigFactory(name='CONFIG_2', value='VALUE 2')
        AppConfigFactory(name='CONFIG_3', value='VALUE 3')
        VisualTokenColorFactory(lower_range=0, upper_range=34, color='#123456', text_color='#f82ab9')
        VisualTokenColorFactory(lower_range=34, upper_range=49, color='#f78f98', text_color='#89f123')
        VisualTokenColorFactory(lower_range=49, upper_range=49, color='#f87ab3', text_color='#abf123')

        url = reverse('api-v2:app-config-list')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'CONFIG_1': 'VALUE 1',
            'CONFIG_2': 'VALUE 2',
            'CONFIG_3': 'VALUE 3',
            'VISUAL_TOKEN_COLORS': [
                {
                    'lower_range': 0,
                    'upper_range': 34,
                    'color': '#123456',
                    'text_color': '#f82ab9'
                },
                {
                    'lower_range': 34,
                    'upper_range': 49,
                    'color': '#f78f98',
                    'text_color': '#89f123'
                },
                {
                    'lower_range': 49,
                    'upper_range': 49,
                    'color': '#f87ab3',
                    'text_color': '#abf123'
                }
            ]
        })
