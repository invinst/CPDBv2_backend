import os

from django.core.management import call_command
from django.test import TestCase, override_settings

from mock import patch, MagicMock, Mock
from robber import expect

from data.factories import OfficerFactory


class UploadOfficerXlsxTestCase(TestCase):
    @override_settings(S3_BUCKET_OFFICER_CONTENT='officer_content_bucket', S3_BUCKET_XLSX_DIRECTORY='xlsx')
    @patch(
        'xlsx.management.commands.upload_officer_xlsx.Pool',
        return_value=MagicMock(__enter__=Mock(return_value=Mock(imap=map)))
    )
    @patch(
        'xlsx.management.commands.upload_officer_xlsx.export_officer_xlsx',
        return_value=['first.xlsx', 'second.xlsx'],
        create=True
    )
    @patch('xlsx.management.commands.upload_officer_xlsx.s3.upload_file')
    def test_upload_officer_xlsx(self, mock_upload_file, mock_export_officer_xlsx, _):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        call_command('upload_officer_xlsx')

        expect(mock_upload_file.call_count).to.eq(6)
        expect(mock_upload_file).to.be.any_call(
            'tmp/1/first.xlsx',
            'officer_content_bucket',
            'xlsx/1/first.xlsx'
        )
        expect(mock_upload_file).to.be.any_call(
            'tmp/1/second.xlsx',
            'officer_content_bucket',
            'xlsx/1/second.xlsx'
        )
        expect(mock_upload_file).to.be.any_call(
            'tmp/2/first.xlsx',
            'officer_content_bucket',
            'xlsx/2/first.xlsx'
        )
        expect(mock_upload_file).to.be.any_call(
            'tmp/2/second.xlsx',
            'officer_content_bucket',
            'xlsx/2/second.xlsx'
        )
        expect(mock_upload_file).to.be.any_call(
            'tmp/3/first.xlsx',
            'officer_content_bucket',
            'xlsx/3/first.xlsx'
        )
        expect(mock_upload_file).to.be.any_call(
            'tmp/3/second.xlsx',
            'officer_content_bucket',
            'xlsx/3/second.xlsx'
        )

        expect(mock_export_officer_xlsx.call_count).to.eq(3)
        expect(mock_export_officer_xlsx).to.be.any_call(officer_1, 'tmp/1')
        expect(mock_export_officer_xlsx).to.be.any_call(officer_2, 'tmp/2')
        expect(mock_export_officer_xlsx).to.be.any_call(officer_3, 'tmp/3')

        expect(os.path.exists('tmp')).to.be.false()
