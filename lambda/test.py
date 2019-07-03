import argparse
import unittest

import boto3
import botocore
from mock import patch
from moto import mock_s3
from robber import expect


class LambdaFunctionTestCase(unittest.TestCase):
    @mock_s3
    def test_s3_mock(self):
        s3_client = boto3.client('s3')
        try:
            s3_client.get_object(
                Bucket='not_existing_bucket',
                Key='not_existing_file.bin'
            )
        except botocore.exceptions.ClientError as e:
            expect(e.response['Error']['Code']).to.eq('NoSuchBucket')

    def test_s3_no_token(self):
        s3_client = boto3.client('s3')
        try:
            s3_client.get_object(
                Bucket='not_existing_bucket',
                Key='not_existing_file.bin'
            )
        except botocore.exceptions.ClientError as e:
            expect(e.response['Error']['Code']).to.eq('InvalidAccessKeyId')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testing lambda packages.')
    parser.add_argument('-s', metavar='S', help='Test directory')
    parser.add_argument('-p', metavar='P', help='Test file pattern')

    args = parser.parse_args()
    start_dir = args.s or './lambda/'
    pattern = args.p or 'test*.py'

    exit_code = 0

    with patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'fake-access-key-id',
        'AWS_SECRET_ACCESS_KEY': 'fake-secret-access-key',
        'AWS_DEFAULT_REGION': 'us-east-2',
    }):
        loader = unittest.TestLoader()
        tests = loader.discover(top_level_dir='./lambda/', start_dir=start_dir, pattern=pattern)
        testRunner = unittest.TextTestRunner()
        result = testRunner.run(tests)

        if result.failures or result.errors:
            exit_code = 1

    exit(exit_code)
