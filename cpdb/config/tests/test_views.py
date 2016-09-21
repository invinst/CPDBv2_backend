from django.test import TestCase, RequestFactory

from mock import patch

from config.views import index


class ViewsTestCase(TestCase):
    def test_index_view(self):
        with patch('config.views.render') as mock_render:
            request = RequestFactory()
            index(request)
            mock_render.assert_called_once_with(request, '/www/static/index.html')
