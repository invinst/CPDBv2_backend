from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_config.factories import VisualTokenColorFactory


class AppConfigTestCase(APITestCase):

    def test_should_return_correct_colors(self):
        VisualTokenColorFactory(lower_range=0, upper_range=34, color='#123456', text_color='#f82ab9')
        VisualTokenColorFactory(lower_range=34, upper_range=49, color='#f78f98', text_color='#89f123')
        VisualTokenColorFactory(lower_range=49, upper_range=49, color='#f87ab3', text_color='#abf123')

        url = reverse('api-v2:app-config-list')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        response_visual_token_colors = response.data['visual_token_colors']
        expect(len(response_visual_token_colors)).to.eq(3)
        expect(response_visual_token_colors).to.eq([
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
        ])
