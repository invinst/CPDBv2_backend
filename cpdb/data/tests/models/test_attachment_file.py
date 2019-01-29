import json

from django.test import override_settings
from django.test.testcases import TestCase
from mock import patch
from robber import expect

from data.factories import AttachmentFileFactory


class AttachmentFileTestCase(TestCase):
    @override_settings(S3_BUCKET_PDF_DIRECTORY='pdf')
    def test_s3_key(self):
        attachment = AttachmentFileFactory(external_id='123')
        expect(attachment.s3_key).to.eq('pdf/123')

    @override_settings(S3_BUCKET_OFFICER_CONTENT='officer-content-test', S3_BUCKET_PDF_DIRECTORY='pdf')
    @patch('data.models.attachment_file.aws')
    def test_upload_to_s3(self, mock_aws):
        attachment = AttachmentFileFactory(
            external_id='123',
            url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
        )

        attachment.upload_to_s3()

        expect(mock_aws.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdf',
            InvokeArgs=json.dumps({
                'url': 'http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf',
                'bucket': 'officer-content-test',
                'key': 'pdf/123'
            })
        )
