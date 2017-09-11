import os
import uuid

from azure.storage.file import FileService


class AzureStorage(object):
    def __init__(self, account_name=None, account_key=None, share=None):
        self._service = FileService(account_name=account_name, account_key=account_key)
        self.share = share
        self._base_path = '/tmp/{share}-{unique_str}'.format(share=share, unique_str=uuid.uuid4())
        self._downloaded = []

        if not os.path.exists(self._base_path):
            os.makedirs(self._base_path)

    def _download(self, folder):
        if folder in self._downloaded:
            return

        download_path = '{base_path}/{folder}'.format(base_path=self._base_path, folder=folder)

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for _file in self._service.list_directories_and_files(self.share, folder):
            file_path = '{download_path}/{file_name}'.format(download_path=download_path, file_name=_file.name)
            self._service.get_file_to_path(self.share, folder, _file.name, file_path)

        self._downloaded.append(folder)

    def path_for(self, resource):
        try:
            folder, name = resource.split('/')
        except ValueError:
            raise Exception('Bad resource name')

        self._download(folder)
        return '{base_path}/{folder}/{name}'.format(base_path=self._base_path, folder=folder, name=name)
