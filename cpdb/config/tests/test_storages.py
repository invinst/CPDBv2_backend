from django.test import SimpleTestCase, override_settings

from mock import patch, Mock
from robber import expect

from config.storages import AzureStorage


@override_settings(
    AZURE_STORAGE_ACCOUNT_NAME='name',
    AZURE_STORAGE_ACCOUNT_KEY='key',
    AZURE_STATICFILES_CONTAINER='static')
class AzureStorageTestCase(SimpleTestCase):
    def test_base_blob_service(self):
        storage = AzureStorage()
        service = Mock()
        with patch('config.storages.BaseBlobService', return_value=service) as BaseBlobServiceMock:
            expect(storage.base_blob_service).to.eq(service)
            BaseBlobServiceMock.assert_called_with('name', 'key')

    def test_block_blob_service(self):
        storage = AzureStorage()
        service = Mock()
        with patch('config.storages.BlockBlobService', return_value=service) as BlockBlobServiceMock:
            expect(storage.block_blob_service).to.eq(service)
            BlockBlobServiceMock.assert_called_with('name', 'key')

    @override_settings(AZURE_STATICFILES_SSL=True)
    def test_azure_protocol_https(self):
        expect(AzureStorage().azure_protocol).to.eq('https')

    @override_settings(AZURE_STATICFILES_SSL=False)
    def test_azure_protocol_http(self):
        expect(AzureStorage().azure_protocol).to.eq('http')

    @patch('config.storages.BaseBlobService')
    @patch('config.storages.ContentFile')
    def test_open(self, ContentFileMock, BaseBlobServiceMock):
        storage = AzureStorage()
        storage._open('abc.css')
        storage.base_blob_service.get_blob_to_bytes.assert_called_with('static', 'abc.css')
        ContentFileMock.assert_called()

    @patch('config.storages.BaseBlobService')
    def test_exists(self, BaseBlobServiceMock):
        storage = AzureStorage()
        storage.base_blob_service.exists.return_value = True
        expect(storage.exists('edf.js')).to.be.true()
        storage.base_blob_service.exists.assert_called_with('static', 'edf.js')

    @patch('config.storages.BaseBlobService')
    def test_delete(self, BaseBlobServiceMock):
        storage = AzureStorage()
        storage.delete('my_file')
        storage.base_blob_service.delete_blob.assert_called_with('static', 'my_file')

    @patch('config.storages.BaseBlobService')
    def test_size(self, BaseBlobServiceMock):
        storage = AzureStorage()
        storage.size('another_file')
        storage.base_blob_service.get_blob_properties.assert_called_with('static', 'another_file')

    @patch('config.storages.BlockBlobService')
    def test_save(self, BlockBlobServiceMock):
        storage = AzureStorage()
        content = Mock(
            file=Mock(content_type='text/html'),
            chunks=Mock(return_value=['a', 'b']))
        name = 'index.html'
        content_settings = Mock()
        with patch('config.storages.ContentSettings', return_value=content_settings) as ContentSettingsMock:
            storage._save(name, content)
            ContentSettingsMock.assert_called_with(content_type='text/html')
            storage.block_blob_service.create_blob_from_bytes.assert_called_with(
                'static', 'index.html', b'ab', content_settings=content_settings)

    @patch('config.storages.BlockBlobService')
    def test_save_other_branch(self, BlockBlobServiceMock):
        storage = AzureStorage()
        content = Mock(
            spec=['read', 'file'],
            read=Mock(return_value='abc'),
            file=Mock(spec=['read']))
        name = 'index.html'
        content_settings = Mock()
        with patch('config.storages.ContentSettings', return_value=content_settings) as ContentSettingsMock:
            storage._save(name, content)
            ContentSettingsMock.assert_called_with(content_type='text/html')
            storage.block_blob_service.create_blob_from_bytes.assert_called_with(
                'static', 'index.html', 'abc', content_settings=content_settings)

    @patch('config.storages.BaseBlobService')
    def test_url(self, BaseBlobServiceMock):
        storage = AzureStorage()
        storage.url('abc.css')
        storage.base_blob_service.make_blob_url.assert_called_with(
            container_name='static',
            blob_name='abc.css',
            protocol='http',
        )

    @patch('config.storages.BaseBlobService')
    def test_get_modified_time(self, BaseBlobServiceMock):
        storage = AzureStorage()
        storage.get_modified_time('admin.js')
        storage.base_blob_service.get_blob_properties.assert_called_with('static', 'admin.js')

    @patch('config.storages.BaseBlobService.get_blob_to_bytes', return_value=Mock(content='blob_bytes'))
    def test_get_bytes(self, BaseBlobServiceMock):
        storage = AzureStorage()
        content_bytes = storage.get_bytes('blob_file')
        expect(content_bytes).to.eq('blob_bytes')
