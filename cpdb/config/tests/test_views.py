from django.test import TestCase, RequestFactory

from mock import patch

from config.views import index_view, officer_view, complaint_view
from data.factories import OfficerFactory
from data.models import OfficerAlias


class IndexViewsTestCase(TestCase):
    def test_render_template(self):
        with patch('config.views.render') as mock_render:
            request_factory = RequestFactory()
            request = request_factory.get('/')
            index_view(request)
            mock_render.assert_called_once_with(request, 'index.html')


class OfficerViewTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_render_template(self):
        with patch('config.views.render') as mock_render:
            request = self.request_factory.get('/')
            officer_view(request)
            mock_render.assert_called_once_with(request, 'index.html')

    def test_redirect(self):
        officer = OfficerFactory(id=3)
        OfficerAlias.objects.create(old_officer_id=2, new_officer=officer)
        with patch('config.views.redirect') as mock_redirect:
            request = self.request_factory.get('/officer/2')
            officer_view(request, officer_id=2)
            mock_redirect.assert_called_once_with('/officer/3', permanent=True)


class ComplaintViewTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_render_template(self):
        with patch('config.views.render') as mock_render:
            request = self.request_factory.get('/')
            complaint_view(request)
            mock_render.assert_called_once_with(request, 'index.html')

    def test_redirect(self):
        officer = OfficerFactory(id=3)
        OfficerAlias.objects.create(old_officer_id=2, new_officer=officer)
        with patch('config.views.redirect') as mock_redirect:
            request = self.request_factory.get('/complaint/123/2/')
            complaint_view(request, officer_id=2, crid=123)
            mock_redirect.assert_called_once_with('/complaint/123/3', permanent=True)
