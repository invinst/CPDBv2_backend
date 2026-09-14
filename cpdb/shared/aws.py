import os

import boto3


class AWS(object):
    def __init__(self):
        self._s3 = None
        self._lambda_client = None

    @property
    def is_configured(self):
        return bool(
            os.environ.get('AWS_ACCESS_KEY_ID')
            and os.environ.get('AWS_SECRET_ACCESS_KEY')
            and os.environ.get('AWS_DEFAULT_REGION')
        )

    @property
    def s3(self):
        if not self._s3:
            self._s3 = boto3.client('s3')
        return self._s3

    @property
    def lambda_client(self):
        if not self._lambda_client:
            self._lambda_client = boto3.client('lambda')
        return self._lambda_client


aws = AWS()
