from unittest import TestCase

import boto3
from moto import mock_s3
from mock import patch, Mock
from robber import expect

from .lambda_function import lambda_handler


class LambdaFunctionTestCase(TestCase):
    @mock_s3
    @patch('upload_pdf.lambda_function.Request', return_value='Request')
    @patch('upload_pdf.lambda_function.urlopen', return_value=Mock(read=Mock(return_value='Data')))
    def test_lambda_handler(self, mock_urlopen, mock_request):
        s3 = boto3.resource('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='officer-content-test')

        lambda_handler(
            event={
                'url': 'https://some/url',
                'key': 'pdf/2641567',
                'bucket': 'officer-content-test',
            },
            context=None
        )

        expect(mock_request).to.be.called_once_with('https://some/url', data=None, headers={'User-Agent': ''})
        expect(mock_urlopen).to.be.called_once_with('Request')

        body = s3.Object('officer-content-test', 'pdf/2641567').get()['Body'].read().decode('utf-8')
        expect(body).to.eq('Data')
