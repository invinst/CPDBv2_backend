from datetime import datetime

from django.conf import settings
from django.template.base import Origin
from django.template.loader import TemplateDoesNotExist
from django.template.loaders.base import Loader

from .storages import AzureStorage


class AzureStorageLoader(Loader):
    _azure_storage = AzureStorage(azure_container=settings.AZURE_TEMPLATE_CONTAINER)
    time_to_live = settings.TEMPLATE_TIME_TO_LIVE

    def __init__(self, *args, **kwargs):
        super(AzureStorageLoader, self).__init__(*args, **kwargs)
        self._templates_dict = dict()
        self._last_retrieve = dict()

    def _is_expired(self, name):
        if name not in self._last_retrieve:
            return True

        return datetime.now() - self._last_retrieve[name] >= self.time_to_live

    def _download_template_content(self, name):
        template_content = self._azure_storage.get_bytes(name)
        self._templates_dict[name] = template_content
        self._last_retrieve[name] = datetime.now()
        return template_content

    def get_template_sources(self, template_name):
        yield Origin(template_name, template_name, loader=self)

    def get_contents(self, origin):
        if not self._is_expired(origin.name) and origin.name in self._templates_dict:
            return self._templates_dict[origin.name]

        if not self._azure_storage.exists(origin.name):
            raise TemplateDoesNotExist(origin)

        return self._download_template_content(origin.name)
