from datetime import timedelta
from time import sleep

from django.test import SimpleTestCase, override_settings
from django.template.base import Origin
from django.template.loader import TemplateDoesNotExist

from mock import patch
from robber import expect

from config.loaders import AzureStorageLoader


@override_settings(TEMPLATE_TIME_TO_LIVE=timedelta(milliseconds=100))
class AzureStorageLoaderTestCase(SimpleTestCase):
    def setUp(self):
        self.loader = AzureStorageLoader(engine=None)

    def test_get_template_sources(self):
        origins = list(self.loader.get_template_sources('home.html'))
        expect(origins).to.have.length(1)
        expect(origins[0].name).to.eq('home.html')
        expect(origins[0].template_name).to.eq('home.html')
        expect(origins[0].loader).to.eq(self.loader)

    @patch('config.loaders.AzureStorage.exists', return_value=True)
    @patch('config.loaders.AzureStorage.get_bytes', return_value='template_content')
    def test_get_contents_from_storage(self, get_bytes_patch, _):
        content = self.loader.get_contents(Origin('home.html'))
        expect(get_bytes_patch).to.be.called_with('home.html')
        expect(content).to.eq('template_content')

    @patch('config.loaders.AzureStorage.exists', return_value=True)
    @patch('config.loaders.AzureStorage.get_bytes', return_value='template_content')
    def test_get_contents_from_memory(self, get_bytes_patch, _):
        content = self.loader.get_contents(Origin('home.html'))
        expect(content).to.eq('template_content')
        get_bytes_patch.reset_mock()

        content = self.loader.get_contents(Origin('home.html'))
        expect(content).to.eq('template_content')
        expect(get_bytes_patch).not_to.be.called()

    @patch('config.loaders.AzureStorage.exists', return_value=False)
    def test_get_contents_does_not_exist(self, _):
        expect(lambda: self.loader.get_contents(Origin('home.html'))).to.throw_exactly(TemplateDoesNotExist)

    @patch('config.loaders.AzureStorage.exists', return_value=True)
    @patch('config.loaders.AzureStorage.get_bytes', return_value='template_content')
    def test_get_contents_from_storage_if_expired(self, get_bytes_patch, _):
        content = self.loader.get_contents(Origin('home.html'))
        expect(content).to.eq('template_content')
        get_bytes_patch.reset_mock()

        sleep(0.11)

        content = self.loader.get_contents(Origin('home.html'))
        expect(content).to.eq('template_content')
        expect(get_bytes_patch).not_to.be.called()
