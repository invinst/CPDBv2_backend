from mock import Mock, patch

from robber import expect

from django.test import SimpleTestCase

from data_importer.base.storage import AzureStorage


class AzureStorageTest(SimpleTestCase):
    @patch('data_importer.base.storage.FileService')
    def test_path_for_raise_exception_if_bad_resource_name(self, mock):
        storage = AzureStorage()
        expect(lambda: storage.path_for('bad/resource/name')).to.throw(Exception)

    @patch('data_importer.base.storage.FileService')
    @patch('data_importer.base.storage.os')
    def test_create_temporary_working_path_if_it_does_not_exist(self, os, service):
        os.path.exists.return_value = False

        AzureStorage()

        expect(os.makedirs).to.be.called()

    @patch('data_importer.base.storage.FileService')
    @patch('data_importer.base.storage.os')
    def test_create_resource_path_if_it_does_not_exist(self, os, service):
        resource = 'folder/name'
        os.path.exists.return_value = False

        storage = AzureStorage()
        storage.path_for(resource)

        expect(os.makedirs.call_count).to.be.equal(2)

    @patch('data_importer.base.storage.FileService')
    @patch('data_importer.base.storage.os')
    def test_download_all_files_in_folder_when_access_a_resource(self, os, service):
        share = 'share'
        resource = 'folder/name'
        os.path.exists.return_value = True
        mock = Mock(list_directories_and_files=Mock(return_value=[
            Mock(name='name'),
            Mock(name='another_name')
        ]))
        service.return_value = mock

        storage = AzureStorage(share=share)
        storage.path_for(resource)

        expect(mock.get_file_to_path.call_count).to.be.equal(2)

        # do not download the resource again
        storage.path_for(resource)
        expect(mock.get_file_to_path.call_count).to.be.equal(2)
