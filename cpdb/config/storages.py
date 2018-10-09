import mimetypes

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings

from azure.storage.blob.models import ContentSettings
from azure.storage.blob.baseblobservice import BaseBlobService
from azure.storage.blob.blockblobservice import BlockBlobService
from azure.common import AzureMissingResourceHttpError


@deconstructible
class AzureStorage(Storage):
    def __init__(self, azure_container=settings.AZURE_STATICFILES_CONTAINER, *args, **kwargs):
        super(AzureStorage, self).__init__(*args, **kwargs)
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.azure_container = azure_container
        self.azure_ssl = settings.AZURE_STATICFILES_SSL
        self._base_blob_service = None
        self._block_blob_service = None

    @property
    def base_blob_service(self):
        if self._base_blob_service is None:
            self._base_blob_service = BaseBlobService(
                self.account_name, self.account_key)
        return self._base_blob_service

    @property
    def block_blob_service(self):
        if self._block_blob_service is None:
            self._block_blob_service = BlockBlobService(
                self.account_name, self.account_key)
        return self._block_blob_service

    @property
    def azure_protocol(self):
        if self.azure_ssl:
            return 'https'
        return 'http' if self.azure_ssl is not None else None

    def _open(self, name, mode="rb"):
        blob = self.base_blob_service.get_blob_to_bytes(self.azure_container, name)
        return ContentFile(blob.content)

    def exists(self, name):
        return self.base_blob_service.exists(self.azure_container, name)

    def delete(self, name):
        try:
            self.base_blob_service.delete_blob(self.azure_container, name)
        except AzureMissingResourceHttpError:  # pragma: no cover
            pass

    def size(self, name):
        blob = self.base_blob_service.get_blob_properties(self.azure_container, name)
        return blob.properties.content_length

    def _save(self, name, content):
        if hasattr(content.file, 'content_type'):
            content_type = content.file.content_type
        else:
            content_type = mimetypes.guess_type(name)[0]

        if hasattr(content, 'chunks'):
            content_data = b''.join(chunk for chunk in content.chunks())
        else:
            content_data = content.read()

        self.block_blob_service.create_blob_from_bytes(
            self.azure_container, name,
            content_data,
            content_settings=ContentSettings(content_type=content_type))
        return name

    def url(self, name):
        return self.base_blob_service.make_blob_url(
            container_name=self.azure_container,
            blob_name=name,
            protocol=self.azure_protocol,
        )

    def get_modified_time(self, name):
        blob = self.base_blob_service.get_blob_properties(
            self.azure_container,
            name
        )
        return blob.properties.last_modified

    def get_bytes(self, name):
        blob = self.base_blob_service.get_blob_to_bytes(self.azure_container, name)
        return blob.content
