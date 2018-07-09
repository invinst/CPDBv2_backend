from mock import patch, Mock

from django.test import override_settings
from django.test.testcases import SimpleTestCase

from robber import expect

from data.migration_utils import csv_from_azure


class CSVFromAzureTestCase(SimpleTestCase):
    block_blob_service = Mock()
    tmp_file = Mock()
    csvfile = Mock(close=Mock())
    reader = Mock()

    @override_settings(DATA_PIPELINE_STORAGE_ACCOUNT_NAME='acc', DATA_PIPELINE_STORAGE_ACCOUNT_KEY='key')
    @patch('data.migration_utils.os')
    @patch('data.migration_utils.BlockBlobService', return_value=block_blob_service)
    @patch('data.migration_utils.NamedTemporaryFile', return_value=tmp_file)
    @patch('data.migration_utils.open', return_value=csvfile)
    @patch('data.migration_utils.DictReader', return_value=reader)
    def test_csv_from_azure(self, DictReader, open, NamedTemporaryFile, BlockBlobService, os):
        self.tmp_file.name = 'xyz123'
        with csv_from_azure('abc.csv') as reader:
            expect(BlockBlobService).to.be.called_with(account_name='acc', account_key='key')
            expect(NamedTemporaryFile).to.be.called_with(suffix='.csv', delete=False)
            expect(self.block_blob_service.get_blob_to_path).to.be.called_with('csv', 'abc.csv', 'xyz123')
            expect(open).to.be.called_with('xyz123')
            expect(DictReader).to.be.called_with(self.csvfile)
            expect(reader).to.equal(self.reader)
        expect(self.csvfile.close).to.be.called()
        expect(os.remove).to.be.called_with('xyz123')
